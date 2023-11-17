let leftMenuBar = document.getElementById("leftmenubar");
let leftMenuBarContent = document.getElementById("leftmenubar-content");
let page_path = document.getElementById("master-page-name");

async function getCarouselItems(queryUrl) {

    let response_data = await fetch(queryUrl);
    let data_json = await response_data.json();
    console.log(data_json);
    const imageList = [];
    data_json.jdata.forEach((item)=>{
        console.log(item);
        imageList.push(item);
    });

    return imageList;

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

async function open_carousel_menu(event) {

    leftMenuBar.style.display = "flex";
    let divTitle = document.createElement("h1");
    divTitle.className = "leftmenu-title";
    divTitle.innerText = "Carousel Editor";
    leftMenuBarContent.appendChild(divTitle);
    let buttonId = event.target.parentNode.id
    console.log(`buttonID=${buttonId}`);
    let carouselId = buttonId.split("-").at(2);
    console.log(`carouselId=${carouselId}`);
    let queryUrl = "/admingetcarousel/" + carouselId;
    console.log(`queryUrl=${queryUrl}`);
    let imageList = await getCarouselItems(queryUrl);
    imageList.forEach((item) => {
        let container = document.createElement('div');
        container.className = "carousel-editor-row";
        let image = document.createElement("img");
        image.src = item.src;
        image.style.maxHeight = "50%";
        image.style.maxWidth = "50%";

        let removeButton = document.createElement("button");
        removeButton.innerHTML = '<span class="material-symbols-outlined">delete</span>';
        removeButton.className = "carousel-image-remove";
        removeButton.addEventListener("click", (event) => {
            fetch("/removecarouselimage", {
                method: "POST",
                body: JSON.stringify({
                    carousel_id: carouselId,
                    image_id: item.id,
                    page_path: page_path.value
                }),
                headers: {
                    "Content-type": "application/json; charset=UTF-8"
                }
            }).then((response) => response.json())
            .then((data) => {
                window.location = data.redirect;
            })
        })

        container.appendChild(image);
        container.appendChild(removeButton);
        leftMenuBarContent.appendChild(container);

        console.log(item);
    })
    const form = document.createElement("form");
    form.method = "POST";
    form.action = "/adminaddcarouselimage";
    form.enctype ="multipart/form-data"

    let encapsulatingLabel = document.createElement("label");
    let newImageBtn = document.createElement("input");
    let carouselIdLbl = document.createElement("input");
    let pagePathLbl = document.createElement("input");
    let uploadParagraph = document.createElement("p");

    newImageBtn.type = "file";
    newImageBtn.style.display = "none";
    newImageBtn.name = "file";
    newImageBtn.id = "new-image-file";

    carouselIdLbl.name = "carousel-id";
    carouselIdLbl.type = "hidden";
    carouselIdLbl.value = `${carouselId}`;
    carouselIdLbl.id = `carousel-id-${carouselId}`;

    pagePathLbl.name = "page-path";
    pagePathLbl.type = "hidden";
    pagePathLbl.value = `${page_path.value}`;
    pagePathLbl.id = `page-path-${page_path.value}`

    uploadParagraph.innerHTML = `<span id="editmenutextspan" class="material-symbols-outlined">upload_file</span>`;
    newImageBtn.addEventListener("change", (event) => {
        form.submit();
    })

    encapsulatingLabel.appendChild(newImageBtn);
    encapsulatingLabel.appendChild(uploadParagraph);
    form.appendChild(carouselIdLbl);
    form.appendChild(pagePathLbl);
    form.appendChild(encapsulatingLabel);
    leftMenuBarContent.appendChild(form);

    let closeLeftMenu = document.createElement("button");
    closeLeftMenu.id = "leftmenu-close";
    closeLeftMenu.innerHTML = '<span class="material-symbols-outlined">close</span>';
    closeLeftMenu.addEventListener("click", (event) => {
        leftMenuBarContent.innerHTML = "";
        leftMenuBar.style.display = "none";
    });
    leftMenuBarContent.appendChild(closeLeftMenu);
}
