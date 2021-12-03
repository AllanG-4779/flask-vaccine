
let editMode = false

const btnEdit = document.querySelector('#btn-edit')
const btn_save = document.querySelector("#btn-save");
btnEdit.addEventListener('click', function(){
   editMode = !editMode
   var inputs = document.querySelectorAll(".editable");
   if(editMode){
      for (var i = 0; i < inputs.length; i++) {
        inputs[i].removeAttribute("disabled");
        
      }
      btnEdit.innerHTML = "Cancel"
      btnEdit.classList.remove('btn-primary')
      btnEdit.classList.add('btn-danger')
      btn_save.removeAttribute('style')
      
      
   }else{
       for (var i = 0; i < inputs.length; i++) {
         inputs[i].disabled=true;
       }
       btnEdit.innerHTML = "Edit info"
       btnEdit.classList.remove('btn-danger')
       btnEdit.classList.add("btn-primary");
       btn_save.setAttribute('style', 'display:none;')
   }
   
})
