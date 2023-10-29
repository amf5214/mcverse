const dropArea2 = document.getElementById("drop-area");
const inputFile2 = document.getElementById("input-file");
const imageView2 = document.getElementById("img-view");

const dropArea = document.getElementById("drop-area2");
const inputFile = document.getElementById("input-file2");
const imageView = document.getElementById("img-view2");

const dropArea3 = document.getElementById("drop-area3");
const inputFile3 = document.getElementById("input-file3");
const imageView3 = document.getElementById("img-view3");

const profileImageForm = document.getElementById("itemimageform");

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
    imageObj.style.maxHeight = "100%";
    imageObj.style.maxWidth = "100%";
    imageObj.style.borderRadius = "50rem";

    let submitButtom = document.createElement("input");
    submitButtom.type = "submit";
    submitButtom.style.margin = "1rem";
    imageView.appendChild(submitButtom);
}

inputFile2.addEventListener("change", uploadImage2);

function uploadImage2() {
    inputFile2.files[0];
    let imgLink = URL.createObjectURL(inputFile2.files[0]);
    // imageView.style.backgroundImage = `url(${imgLink})`;
    imageView2.textContent = "";
    imageView2.style.border = 0;
    let imageObj = document.createElement('img');
    imageObj.src = `${imgLink}`;
    imageView2.appendChild(imageObj);
    imageObj.style.maxHeight = "100%";
    imageObj.style.maxWidth = "100%";
    imageObj.style.borderRadius = "50rem";

    let submitButtom = document.createElement("input");
    submitButtom.type = "submit";
    submitButtom.style.margin = "1rem";
    imageView2.appendChild(submitButtom);
}

inputFile3.addEventListener("change", uploadImage3);

function uploadImage3() {
    inputFile3.files[0];
    let imgLink = URL.createObjectURL(inputFile3.files[0]);
    // imageView.style.backgroundImage = `url(${imgLink})`;
    imageView3.textContent = "";
    imageView3.style.border = 0;
    let imageObj = document.createElement('img');
    imageObj.src = `${imgLink}`;
    imageView3.appendChild(imageObj);
    imageObj.style.maxHeight = "100%";
    imageObj.style.maxWidth = "100%";
    imageObj.style.borderRadius = "50rem";

    let submitButtom = document.createElement("input");
    submitButtom.type = "submit";
    submitButtom.style.margin = "1rem";
    imageView3.appendChild(submitButtom);
}


showmenubtn = document.getElementById("openclosebtn")
editingmenu = document.getElementById("editing-menu")
editmenutextspan = document.getElementById("editmenutextspan")

function showftn() {
    if(editmenutextspan.textContent == "right_panel_close") {
        editmenutextspan.textContent = "right_panel_open";
        editingmenu.style.visibility = "hidden";
    }

    else {
        editmenutextspan.textContent = "right_panel_close";
        editingmenu.style.visibility = "visible";
    }
}