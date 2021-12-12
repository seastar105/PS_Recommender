var idField = document.querySelector('.idField');
var idSubmit = document.querySelector('.idSubmit');

idField.addEventListener('keypress', function(key) {
  if(key.key != 'Enter') return;

  const id = idField.value;
  if (id == '') return;
  //window.open("/user/?user=" + id);
  location.href = "/user/?id=" + id;
});

idSubmit.addEventListener('click', function() {
  const id = idField.value;
  if (id == '') return;
  //window.open("/user/?user=" + id);
  location.href = "/user/?id=" + id;
});