let draggables = document.getElementsByClassName('draggable-obj');
const modified = [];
const modified_data = [];

for(const element of draggables) {

    element.addEventListener('dragstart', (event) => {
        console.log('dragstart event fired');
        event.dataTransfer.setData('text/plain' , event.target.innerText);
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
