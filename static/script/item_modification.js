const editable_boxes = document.getElementsByClassName("editable-item");
let id = document.getElementById("item-num-db");

console.log("Item id: " + id.innerText);

function addListener(element) {
    element.addEventListener("focusout", function() {
        let attribute = element.id;
        let newValuedata = element.innerText.split(": ");
        console.log(`innerText=${element.innerText}; newValuedata=${newValuedata.at(0)}`);
        let newValue;
        if(newValuedata.length > 1) {
            newValue = newValuedata[1];
        } else {
            newValue = newValuedata[0];
        }

        if(attribute == "item_title") {
            newValue = newValue.split(" rocket_launch")[0]
        }

        if(attribute == "item_type") {
            newValue = element.value;
            console.log(`element_value=${element.value}`)
            console.log(`element_text=${element.text}`)
        }
        sendData("/updateitem/" + id.innerText, {"item":id.innerText, "attribute": attribute, "newValue": newValue});
    })
};

function sendData(path, parameters, method='post') {

    const form = document.createElement('form');
    form.method = method;
    form.action = path;
    document.body.appendChild(form);
  
    for (const key in parameters) {
        const formField = document.createElement('input');
        formField.type = 'hidden';
        formField.name = key;
        formField.value = parameters[key];
  
        form.appendChild(formField);
    }
    form.submit();

}

for(let element of editable_boxes) {
    addListener(element);
}

function open_video_edit() {
    let videoLink = document.createElement("h3");
    videoLink.id = "iframe_video_link";
    videoLink.className = "editable-item iframe-link";
    videoLink.contentEditable = "true";
    videoLink.innerText = 'Text';
    videoLink.style.cursor = "text";
    addListener(videoLink);
    let box = document.getElementById("editing-menu");
    box.appendChild(videoLink);
}