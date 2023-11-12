let draggables = document.getElementsByClassName('draggable-obj');
let dropzones = document.getElementsByClassName('dropzone');
const modified = [];
const modified_data = [];

for(const element of draggables) {

    element.addEventListener('dragstart', (event) => {
        console.log('dragstart event fired');
        event.dataTransfer.setData('text/plain' , "" + event.target.innerText + "//" + event.target.id);
    })

    element.addEventListener('dragend', (event) => {
        console.log('dragend event fired');
        console.log(modified_data);
        modified_data.forEach( x => {
            let obj = document.getElementById(x.at(0));
            obj.style.border = x.at(1);
        });

        modified.splice(0, modified.length);
        modified_data.splice(0, modified_data.length);
        event.preventDefault();  
    })

}

for(const dropzone of dropzones) {
    dropzone.addEventListener('dragover', (event) => {
        console.log('dragover event fired');
        if(!modified.includes(event.target.id)) {
            modified_data.push([event.target.id, event.target.style.border]);
            modified.push(event.target.id);
        }
        event.target.style.border = 'dashed 2px white';
        event.preventDefault();
    })

    dropzone.addEventListener('drop', (event) => {
        console.log('drop event fired');
        let elementType = event.dataTransfer.getData("text/plain");
        let elementData = elementType.split("//");
        let placement_order = -1;
        if(elementData.length > 1) {
            placement_order = elementData.at(1).split("-").at(1);
            placement_order = parseInt(placement_order);
            placement_order += 1;
        }
        let pageId = document.getElementById("master-page-id").value;
        let pagePath = document.getElementById("master-page-name").value

        event.preventDefault();

        if(elementData.at(0) == "Section") {
            if(event.target.className == "dropzone") {
                window.location.replace(`/learningpage/admin/newdiv/${pagePath}/${pageId}/${placement_order}`);
            }
        }  
    })
}
