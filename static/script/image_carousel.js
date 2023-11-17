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

        leftMenuBarContent.appendChild(container);

        console.log(item);
    })
}
