var eliminando;

function cambiaRuta(ruta) {
    form = document.querySelector("form");
    form.action = ruta;
    eliminando=false;
    if (ruta =="/producto/delete") {
        eliminando=true;
    }
}

function confirmarBorrado() {
    if (eliminando){
        return confirm("Desea eliminar el registro?");
    }
}