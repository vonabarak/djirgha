import json
from django.views.generic import TemplateView, View
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import resolve_url
from djirgha.models import Board


class HotSeatView(TemplateView):
    template_name = 'board.html'

    def get_context_data(self, **kwargs):
        return {"board": Board}

    def get(self, request, *args, **kwargs):
        response = super(HotSeatView, self).get(request, *args, **kwargs)
        board_id = request.session.get("board_id")
        if board_id is None:
            board = Board.objects.create()
            request.session["board_id"] = board.id
        else:
            try:
                Board.objects.get(pk=board_id)
            except Board.DoesNotExist:
                board = Board.objects.create()
                request.session["board_id"] = board.id

        if request.GET.get("newgame"):
            board = Board.objects.create()
            request.session["board_id"] = board.id
            return HttpResponseRedirect(resolve_url("hot-seat"))
        return response


class TurnView(View):
    def get(self, request, punkt):
        board, _ = Board.objects.get_or_create(pk=request.session["board_id"])
        success = board.make_turn(punkt_name=punkt)
        if success:
            message = board.message
        else:
            message = f"Invalid move. {board.message}"
        response = {
            "punkts": board.dict,
            "message": message
        }
        return HttpResponse(json.dumps(response))


class CurrentView(View):
    def get(self, request):
        board, _ = Board.objects.get_or_create(pk=request.session["board_id"])
        response = {
            "punkts": board.dict,
            "message": "Board refreshed.\n" + board.message
        }
        return HttpResponse(json.dumps(response))
