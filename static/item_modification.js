const editable_boxes = document.getElementsByClassName("editable-item");
let id = document.getElementById("item-num-db");

console.log("Item id: " + id.innerText);

function addListener(element) {
    element.addEventListener("focusout", function() {
        let attribute = element.id;
        let newValuedata = element.innerText.split(": ");
        let newValue;
        if(newValuedata.length > 1) {
            newValue = newValuedata[1];
        } else {
            newValue = newValuedata[0];
        }

        if(attribute == "item_title") {
            newValue = newValue.split(" rocket_launch")[0]
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

