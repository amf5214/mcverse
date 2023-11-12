const editable_boxes = document.getElementsByClassName("editable-item");
const pagePath = document.getElementById("master-page-name").value
function addListener(element) {
    element.addEventListener("focusout", function() {
        let attribute = element.id;
        let newValuedata = element.innerText;
        attributePieces = attribute.split("-");

        if(attributePieces.at(1) == "title") {
            newValuedata = newValuedata.split("rocket_launch")[0].trim()
        }

        if(attributePieces.at(1) == "title" || attributePieces.at(1) == "text") {
            if(attributePieces.at(0) == "page" || attributePieces.at(0) == "div" || attributePieces.at(0) == "element") {
                sendData(`/updatelearningitem`, {"page_path": pagePath, "item":attributePieces.at(2), "container": attributePieces.at(0), "attribute": attributePieces.at(1), "newValue": newValuedata});
            }
        }
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

const dropArea = document.getElementById("drop-area");
const inputFile = document.getElementById("input-file");
const imageView = document.getElementById("img-view");
const profileImageForm = document.getElementById("pageelementimageupdate");

inputFile.addEventListener("change", uploadImage);

function uploadImage() {
    inputFile.files[0];
    let imgLink = URL.createObjectURL(inputFile.files[0]);
    // imageView.style.backgroundImage = `url(${imgLink})`;
    imageView.textContent = "";
    imageView.style.border = 0;
    let imageObj = document.createElement('img');
    imageObj.src = `${imgLink}`;
    imageView.appendChild(imageObj);
    imageObj.style.maxHeight = "50%";
    imageObj.style.maxWidth = "50%";

    let submitButtom = document.createElement("input");
    submitButtom.type = "submit";
    submitButtom.style.margin = "1rem";
    imageView.appendChild(submitButtom);
}