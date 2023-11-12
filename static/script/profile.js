const dropArea = document.getElementById("drop-area");
const inputFile = document.getElementById("input-file");
const imageView = document.getElementById("img-view");
const profileImageForm = document.getElementById("profileimageform");

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