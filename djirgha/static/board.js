/*
boardParams example:
{
  height: 828,
  width: 828,
  lanes: [
    [[30, 30], [798, 30]],
    [[798, 30], [798, 798]],
    ...
  ],
  punkts: {
    a1: {
      x: 30,
      y: 30,
      color: "#808080"
    },
    a2: {
      x: 414,
      y: 30,
      color: "#808080"
    },
    ...
  }
}
*/

function drawLane(context, lane){
  context.moveTo(lane[0][0], lane[0][1]);
  context.lineTo(lane[1][0], lane[1][1]);
}

function drawBoard(canvas, boardParams){
  const context = canvas.getContext("2d");
  context.beginPath();
  context.rect(0, 0, boardParams.width, boardParams.height);
  context.fillStyle = "#808080";
  context.fill();

  boardParams.lanes.forEach(function(item) {
    drawLane(context, item)
  });
  context.stroke();
  return context;
}

function fillPunkt(context, punkt, color, border){
  context.fillStyle = color;
  context.beginPath();
  context.arc(punkt.x, punkt.y, 15, 0, 2*Math.PI);
  context.fill();
  punkt.color = color;
}
function borderPunkt(context, punkt, color){
  context.beginPath();
  context.arc(punkt.x, punkt.y, 15, 0, 2*Math.PI);
  context.lineWidth = 3;
  context.strokeStyle = color;
  context.stroke();
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function blinkPunkt(context, punkt){
    fillPunkt(context, punkt, "#ff0000");
    await sleep(200);
    fillPunkt(context, punkt, "#00ff00");
    await sleep(200);
    fillPunkt(context, punkt, "#0000ff");
    await sleep(200);
}

async function drawPunkts(context, boardParams, state) {
  const punkts = boardParams.punkts;
  let p;
  for (let punkt_name in punkts) {
    if (state[punkt_name].blink) {
      p = blinkPunkt(context, punkts[punkt_name]);
    }
  }
  if (p) await p;

  for (let punkt_name in punkts) {
    fillPunkt(context, punkts[punkt_name], state[punkt_name].color);
    borderPunkt(context, punkts[punkt_name], state[punkt_name].border);
  }
}

function logMessage(message) {
  const log = document.getElementById("log");
  const p = document.createElement("p");
  const text = document.createTextNode(message);
  p.appendChild(text);
  log.prepend(p);
}


function makeRequest(context, boardParams, url) {
  const xhr = new XMLHttpRequest();
  xhr.open("GET", url);
  xhr.send();
  xhr.onreadystatechange = (_event) => {if (xhr.readyState === 4) {
    const response = JSON.parse(xhr.responseText);
    console.log(response);
    drawPunkts(context, boardParams, response.punkts);
    logMessage(response.message);
  }};
}


function getCurrentStatus(context, boardParams) {
  const url ="/current/";
  makeRequest(context, boardParams, url);
}

function eventLisener(event, context, boardParams){
  const size = 40;
  for (let punkt_name in boardParams.punkts) {
    // check which punkt was clicked
    const punkt = boardParams.punkts[punkt_name];
    const x_ = punkt.x+size >= event.layerX && event.layerX >= punkt.x-size;
    const y_ = punkt.y+size >= event.layerY && event.layerY >= punkt.y-size;
    if (x_ && y_) {
      makeRequest(context, boardParams, "/turn/" + punkt_name);
    }
  }
}
