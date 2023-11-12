const editable_boxes = document.getElementsByClassName("editable-item");

function addListener(element) {
    element.addEventListener("focusout", function() {
        let attributeData = element.id.split("-");
        let attribute = attributeData[0];
        let id = attributeData[1];
        let newValue = element.innerText;
        console.log("<"+ id + ", " + attribute + ">");
        sendData("/updateitem/" + id, {"item":id.innerText, "attribute": attribute, "newValue": newValue});
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

