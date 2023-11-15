const editable_boxes = document.getElementsByClassName("editable-item");
const element_containers = document.getElementsByClassName("element-container");
const up_buttons = document.getElementsByClassName("up-buttons");
const down_buttons = document.getElementsByClassName("down-buttons");
const pagePath = document.getElementById("master-page-name").value;
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

function addMoveUpDownBtns(div, elementId) {
    let id_details = div.id;
    id_details = id_details.split("-");

    let container = document.createElement("div");
    container.className = "updownbuttons";
    container.id = `updownbutton_div-${elementId}`;

    let upbutton = document.createElement("button");
    let downbutton = document.createElement("button");

    upbutton.className = "up-buttons";
    upbutton.id = `${id_details.at(2)}/${id_details.at(1)}`
    downbutton.className = "down-buttons";
    downbutton.id = `${id_details.at(2)}/${id_details.at(1)}`

    upbutton.innerHTML = `<span id="editmenutextspan" class="material-symbols-outlined">arrow_upward</span>`;
    downbutton.innerHTML = `<span id="editmenutextspan" class="material-symbols-outlined">arrow_downward</span>`;

    container.appendChild(upbutton);
    container.appendChild(downbutton);

    div.appendChild(container);

}

for(let element of editable_boxes) {
    addListener(element);
}

for(let div of element_containers) {
    let elementId = div.id.split("-").at(1);
    addMoveUpDownBtns(div, elementId);
}

for(let button of up_buttons) {
    button.addEventListener("click", function() {
        console.log("onclick fired");
        console.log(`button id=${button.id}`);
        console.log(`split id=${button.id.split("/")}`);
        const pagePath = document.getElementById("master-page-name").value;
        window.location.href = `/movelearningelement/${pagePath}/${button.id.split("/").at(1)}/up`;
    });
}

for(let button1 of down_buttons) {
    button1.addEventListener("click", function() {
        console.log("onclick fired");
        console.log(`button id=${button1.id}`);
        console.log(`split id=${button1.id.split("/")}`);
        const pagePath = document.getElementById("master-page-name").value;
        window.location.href = `/movelearningelement/${pagePath}/${button1.id.split("/").at(1)}/down`;
    });
}

const fileInputs = document.getElementsByClassName("file-inputs");
console.log(`File inputs = {${fileInputs}}`);

function uploadImage(input) {
    input.addEventListener("change", function() {
        input.files[0];
        let imgLink = URL.createObjectURL(input.files[0]);
        let elementId = input.id;
        let pageElementId = elementId.split("-").at(1);
        let imageView = document.getElementById("img_view-"+pageElementId);
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


    })
}

for(input of fileInputs) {
    uploadImage(input);
}