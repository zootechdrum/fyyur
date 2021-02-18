window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};


const deleteButtons = document.getElementsByClassName("btn-danger")


for (let item of deleteButtons) {
 item.addEventListener('click',deleteVenue);
}

  function deleteVenue() {
    const id = this.getAttribute('data-id')

            fetch('/venues/' + id, {
            method: 'DELETE',
        }).catch(err => {
            console.log(err)
        })
}

