from django.db import models


class Punkt(models.SmallIntegerField):

    def __init__(self, name: str, x, y):
        super().__init__(name=name, default=0)
        self.name = name
        self.x = x
        self.y = y

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs['x'] = self.x
        kwargs['y'] = self.y
        kwargs['name'] = self.name
        kwargs.pop('default')
        return name, path, args, kwargs


class Board(models.Model):
    padding = 30
    width = 768 + (padding * 2)
    height = width

    efw = width - padding * 2  # effective width
    efh = height - padding * 2  # effective height

    # 1st layer
    a1 = Punkt('a1', padding, padding)
    a2 = Punkt('a2', width/2, a1.y)
    a3 = Punkt('a3', width-padding, a1.y)
    a4 = Punkt('a4', a3.x, height/2)
    a5 = Punkt('a5', a3.x, height-padding)
    a6 = Punkt('a6', a2.x, a5.y)
    a7 = Punkt('a7', a1.x, a5.y)
    a8 = Punkt('a8', a1.x, a4.y)
    # 2nd layer
    b1 = Punkt('b1', a1.x + efw / 4, a1.y + efh / 4)
    b2 = Punkt('b2', a2.x, b1.y)
    b3 = Punkt('b3', a3.x - efw / 4, b1.y)
    b4 = Punkt('b4', b3.x, a4.y)
    b5 = Punkt('b5', b3.x, a5.y - efh / 4)
    b6 = Punkt('b6', b2.x, b5.y)
    b7 = Punkt('b7', b1.x, b5.y)
    b8 = Punkt('b8', b1.x, b4.y)
    # 3rd layer
    c1 = Punkt('c1', b1.x + efw / 8, b1.y + efh / 8)
    c2 = Punkt('c2', b3.x - efw / 8, c1.y)
    c3 = Punkt('c3', c2.x, b5.y - efh / 8)
    c4 = Punkt('c4', c1.x, c3.y)

    punkts = [
        a1, a2, a3, a4, a5, a6, a7, a8,  # 1st layer
        b1, b2, b3, b4, b5, b6, b7, b8,  # 2nd layer
        c1, c2, c3, c4  # 3rd layer
    ]

    # 1st layer
    l01 = [a1, a2, a3]
    l02 = [a3, a4, a5]
    l03 = [a5, a6, a7]
    l04 = [a7, a8, a1]

    # 2nd layer
    l05 = [b1, b2, b3]
    l06 = [b3, b4, b5]
    l07 = [b5, b6, b7]
    l08 = [b7, b8, b1]

    # 1st and 2nd layers
    l09 = [a8, b1, a2]
    l10 = [a2, b3, a4]
    l11 = [a4, b5, a6]
    l12 = [a6, b7, a8]

    # 2nd and 3rd layers
    l13 = [b8, c1, b2]
    l14 = [b2, c2, b4]
    l15 = [b4, c3, b6]
    l16 = [b6, c4, b8]

    # diagonal lanes
    l17 = [a1, b1, c1]
    l18 = [a3, b3, c2]
    l19 = [a5, b5, c3]
    l20 = [a7, b7, c4]

    lanes = [
        l01, l02, l03, l04, l05, l06, l07, l08, l09, l10,
        l11, l12, l13, l14, l15, l16, l17, l18, l19, l20
    ]

    # 1 - white player places a white button
    # 2 - white player removes a black button
    # 3 - white player moves a white button
    # 4 - white player places moved button
    # 5 - white player won, game over
    # same values with minus sign for black player
    state = models.SmallIntegerField(default=1)

    # count of matched three-in-row lanes at last turn
    # need for stage 2
    match = models.PositiveSmallIntegerField(default=0)

    # button position at last turn
    # need for stage 4
    prev_turn = models.CharField(
        max_length=2,
        choices=[(p.name, p.name) for p in punkts],
        null=True
    )

    # count of buttons of each player
    # need for stage 1
    black = models.PositiveSmallIntegerField(default=10)
    white = models.PositiveSmallIntegerField(default=10)

    @classmethod
    def punkt_lanes(cls, punkt_name):
        return [l for l in cls.lanes if punkt_name in [p.name for p in l]]

    @classmethod
    def punkt_neighbours(cls, punkt_name):
        neighbours = []
        for lane in cls.punkt_lanes(punkt_name):
            lane_punkts = [p.name for p in lane]
            punkt_pos = lane_punkts.index(punkt_name)
            for i, p in enumerate(lane_punkts):
                if abs(punkt_pos - i) == 1:
                    neighbours.append(p)
        return neighbours

    @property
    def player_value(self):
        """returns 1 for whites turn and -1 for blacks turn"""
        if self.state > 0:
            return 1
        else:
            return -1

    @property
    def abs_turn(self):
        return abs(self.state)

    def check_lanes(self, punkt_name):
        """checks whether three buttons in a line appeared after turn"""
        return [
            lane for lane in Board.punkt_lanes(punkt_name)
            if abs(sum([getattr(self, p.name) for p in lane])) == 3
        ]

    def validate_turn_1(self, punkt_name) -> bool:
        punkt_value = getattr(self, punkt_name)
        # punkt must be empty
        if punkt_value == 0:
            return True
        return False

    def validate_turn_2(self, punkt_name) -> bool:
        punkt_value = getattr(self, punkt_name)
        # punkt must be filled with enemy's button
        if self.state * punkt_value < 0:
            return True
        return False

    def validate_turn_3(self, punkt_name) -> bool:
        punkt_value = getattr(self, punkt_name)
        # punkt must be filled with player's button
        if self.state * punkt_value <= 0:
            return False
        # at least one empty neighbour
        for p in Board.punkt_neighbours(punkt_name):
            if getattr(self, p) == 0:
                return True
        return False

    def validate_turn_4(self, punkt_name) -> bool:
        punkt_value = getattr(self, punkt_name)
        # punkt must be near prev_turn and empty
        if punkt_value != 0:
            return False
        if punkt_name in Board.punkt_neighbours(self.prev_turn):
            return True
        return False

    @staticmethod
    def validate_turn_5(_) -> bool:
        return False

    def validate_turn(self, punkt_name) -> bool:
        validation_func = getattr(self, f"validate_turn_{self.abs_turn}")
        return validation_func(punkt_name)

    @property
    def valid_turns(self):
        return list(filter(self.validate_turn, [p.name for p in Board.punkts]))

    def make_turn_1(self, punkt_name):
        setattr(self, punkt_name, self.player_value)
        if self.state > 0:
            self.white -= 1
        else:
            self.black -= 1
        self.match = len(self.check_lanes(punkt_name))

    def make_turn_2(self, punkt_name):
        setattr(self, punkt_name, 0)
        self.match -= 1

    def make_turn_3(self, punkt_name):
        setattr(self, punkt_name, 0)

    def make_turn_4(self, punkt_name):
        setattr(self, punkt_name, self.player_value)
        self.match = len(self.check_lanes(punkt_name))

    @staticmethod
    def make_turn_5(_):
        pass

    def make_turn(self, punkt_name):
        turn_func = getattr(self, f"make_turn_{self.abs_turn}")
        old_state = self.state
        if self.validate_turn(punkt_name):
            turn_func(punkt_name)

            if self.abs_turn == 3:
                self.state = 4 * self.player_value
            elif self.match and self.abs_turn in [1, 2, 4]:
                self.state = 2 * self.player_value
            elif self.white == 0 and self.black == 0:
                self.state = -3 * self.player_value
            else:
                self.state = -1 * self.player_value

            self.prev_turn = punkt_name

            if not self.valid_turns:
                self.state = -5 * self.player_value

            last_turn = (
                Turn.objects.filter(board=self).order_by("number").last()
            )
            if last_turn:
                turn_number = last_turn.number + 1
            else:
                turn_number = 1
            Turn.objects.create(
                board=self,
                number=turn_number,
                new_state=self.state,
                old_state=old_state,
                punkt=punkt_name,
                match=self.match,
            )
            self.save()
            return True
        else:
            return False

    @staticmethod
    def punkt_color(punkt_value):
        if punkt_value == 0:
            return '#808080'
        elif punkt_value == 1:
            return '#ffffff'
        elif punkt_value == -1:
            return '#000000'

    def punkt_border(self, punkt_name):
        # punkt_value = getattr(self, punkt_name)
        # border_inverted = self.punkt_color(-punkt_value),
        return "#00ff00" if punkt_name in self.valid_turns else "#404040"

    @property
    def dict(self):
        blink_lanes = self.check_lanes(self.prev_turn)
        blink_punkts = [p.name for lane in blink_lanes for p in lane]
        return {
            i.name: {
                "color": self.punkt_color(getattr(self, i.name)),
                "border": self.punkt_border(i.name),
                "blink": i.name in blink_punkts
            }
            for i in Board.punkts
        }

    @property
    def message(self):
        if self.state > 0:
            player = "Whites"
        else:
            player = "Blacks"
        if self.abs_turn == 1:
            return f"{player} places a button"
        elif self.abs_turn == 2:
            return f"{player} removes a button"
        elif self.abs_turn == 3:
            return f"{player} takes a button to move"
        elif self.abs_turn == 4:
            return f"{player} moves a button"
        elif self.abs_turn == 5:
            return f"{player} won!"


class Turn(models.Model):
    class Meta:
        unique_together = (("board", "number"), )

    board = models.ForeignKey(
        "Board", on_delete=models.CASCADE, related_name="turns"
    )
    number = models.PositiveSmallIntegerField()
    old_state = models.SmallIntegerField()
    new_state = models.SmallIntegerField()
    punkt = models.CharField(
        max_length=2,
        choices=[(p.name, p.name) for p in Board.punkts],
        null=True
    )
    match = models.PositiveSmallIntegerField(default=0)
