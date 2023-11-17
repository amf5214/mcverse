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
