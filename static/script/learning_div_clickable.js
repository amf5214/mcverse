let linkDivs = document.getElementsByClassName('link');

function onClickButton(event) {
    let senderDiv = event.target;
    let nodes = senderDiv.childNodes;
    let linkLabel = null;
    for (let node of nodes) {
        if(node.className == 'linklabel') {
            linkLabel = node;
        }
    }
    if(linkLabel != null) {
        window.location = '/learn/' + linkLabel.href.split('/learn/').at(1);
    }
  }

for (let div of linkDivs) {
    div.addEventListener('click', onClickButton);
}