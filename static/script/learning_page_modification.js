const editableBoxes = document.getElementsByClassName("editable-item");
const elementContainers = document.getElementsByClassName("element-container");
const userCreatedDivs = document.getElementsByClassName("user-created-div");
const upButtons = document.getElementsByClassName("up-buttons");
const downButtons = document.getElementsByClassName("down-buttons");
const pagePath = document.getElementById("master-page-name").value;
function addListener(element) {
    element.addEventListener("focusout", function() {
        let attribute = element.id;
        let newValuedata = element.innerText;
        attributePieces = attribute.split("-");
        if(attributePieces.at(1) == "title") {
            newValuedata = newValuedata.split("rocket_launch")[0].trim();
            let valueData2 = newValuedata.split("expand_circle_right");
            if(valueData2.length > 1) {
                newValuedata = valueData2.at(1);
            }
        }

        if(attributePieces.at(1) == "title" || attributePieces.at(1) == "text") {
            if(attributePieces.at(0) == "page" || attributePieces.at(0) == "div" || attributePieces.at(0) == "element") {
                // sendData(`/updatelearningitem`, {"page_path": pagePath, "item":attributePieces.at(2), "container": attributePieces.at(0), "attribute": attributePieces.at(1), "newValue": newValuedata});
                sendPost('/updatelearningitem2', {page_path: pagePath, item: attributePieces.at(2), container: attributePieces.at(0), attribute: attributePieces.at(1), newValue: newValuedata});
            }
        }
    })
};

function sendPost(url, body) {
    fetch(url, {
        method: "POST",
        body: JSON.stringify(body),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    }).then((response) => response.json())
    .then((data) => {
       console.log(data.fulfillable);
    })
}

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

function addMoveUpDownBtns(div) {
    let id_details = div.id;
    id_details = id_details.split("-");
    let itemId = id_details.at(1);

    let container = document.createElement("div");
    container.className = "updownbuttons";
    container.id = `updownbutton_div-${itemId}`;

    let upbutton = document.createElement("button");
    let downbutton = document.createElement("button");

    upbutton.className = "up-buttons";
    upbutton.id = `upbutton/${itemId}/${div.className}`;
    downbutton.className = "down-buttons";
    downbutton.id = `downbutton/${itemId}/${div.className}`;

    upbutton.innerHTML = `<span id="editmenutextspan" class="material-symbols-outlined">arrow_upward</span>`;
    downbutton.innerHTML = `<span id="editmenutextspan" class="material-symbols-outlined">arrow_downward</span>`;

    container.appendChild(upbutton);
    container.appendChild(downbutton);

    div.appendChild(container);

}

for(let element of editableBoxes) {
    addListener(element);
}

for(let div of elementContainers) {
    addMoveUpDownBtns(div);
}

for(let div of userCreatedDivs) {
    addMoveUpDownBtns(div);
}

for(let button of upButtons) {
    button.addEventListener("click", function() {
        console.log("onclick fired");
        let buttonId = button.id.split("/");
        console.log(`split id=${button.id.split("/")}`);
        const pagePath = document.getElementById("master-page-name").value;
        if(buttonId.at(2).split(" ").includes("user-created-div")) {
            window.location.href = `/movelearningdiv/${pagePath}/${buttonId.at(1)}/up`;
        } else {
            window.location.href = `/movelearningelement/${pagePath}/${buttonId.at(1)}/up`;
        }
        
    });
}

for(let button1 of downButtons) {
    button1.addEventListener("click", function() {
        console.log("onclick fired");
        let buttonId = button.id.split("/");
        console.log(`split id=${button.id.split("/")}`);
        const pagePath = document.getElementById("master-page-name").value;
        if(buttonId.at(2).split(" ").includes("user-created-div")) {
            window.location.href = `/movelearningdiv/${pagePath}/${buttonId.at(1)}/down`;
        } else {
            window.location.href = `/movelearningelement/${pagePath}/${buttonId.at(1)}/down`;
        }
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