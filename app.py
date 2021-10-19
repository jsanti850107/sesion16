from flask import Flask, render_template as render,request,flash, session,redirect
import sqlite3
import os
from werkzeug.utils import escape

from wtforms import meta
from forms.formularios import Registro,Login,Productos
import hashlib


app=Flask(__name__)
app.secret_key= os.urandom(24)

#api para registrar los usuarios
@app.route("/registro",methods=["GET","POST"])
def registrar():
    frm=Registro()
    if frm.validate_on_submit():
        username = frm.username.data
        correo = frm.correo.data
        nombre = frm.nombre.data
        password = frm.password.data
        #cifra la contraseña
        encrip = hashlib.sha256(password.encode('utf-8'))
        pass_enc = encrip.hexdigest()
        #conecta a la base de datos
        with sqlite3.connect("vacunacion.db") as con:
            # crea un cursor para manipular la base de datos
            cur=con.cursor()
            #prepara sentencia SQL, preferiblemente no concatenar
            cur.execute("INSERT INTO usuarios(nombre,username,correo,password)values(?,?,?,?)",(nombre,username,correo,pass_enc))
            #se ejecuta la sentencia
            con.commit()
            return "guardado con exito <a href='/'>HOME</a>"
    return render("registro.html",frm=frm)

@app.route("/",methods=["GET","POST"])
def home():
    frm=Login()
    if frm.validate_on_submit():
        #escape para quitar caracteres especiales
        username=escape(frm.username.data)
        password=escape(frm.password.data)
           #cifra la contraseña
        encrip = hashlib.sha256(password.encode('utf-8'))
        pass_enc = encrip.hexdigest()
        #conecta a la base de datos
        with sqlite3.connect("vacunacion.db") as con:
            con.row_factory = sqlite3.Row
            cur=con.cursor()
            cur.execute("SELECT * FROM usuarios WHERE username =? AND password=?",[username,pass_enc])
            row=cur.fetchone()
            if row:
                session['usuario']=username
                session['perfil']=row['perfil']
                if row['perfil']==1:
                    return "Hola Admin"
                elif row['perfil']==2:
                    return redirect("/productos")
                
            else: 
                return "Usuario/Password incorrecto"

    return render("login.html",frm=frm)

@app.route("/usuario/listar",methods=["GET","POST"])
def usuario_listar():
    with sqlite3.connect("vacunacion.db") as con:
        con.row_factory=sqlite3.Row #vista de diccionario
        cur=con.cursor()
        cur.execute("SELECT * FROM usuarios")
        rows=cur.fetchall()
        return render("lista-usuarios.html",rows=rows)

@app.route("/usuario/eliminar",methods=["GET","POST"])
def eliminar():
    frm=Registro()

    if request.method=="POST":
        username=frm.username.data
        with sqlite3.connect("vacunacion.db") as con:
            cur=con.cursor()
            cur.execute("DELETE FROM usuarios WHERE username=?",[username])
            con.commit()
            return "usuario Eliminado"
    return render("eliminar-usuario.html",frm=frm)

@app.route("/productos")
def productos():
    #verifica usuario logueado
    if 'usuario' in session:
        frm = Productos()
        return render("productos.html", frm=frm)
    else:
        return redirect("/")
    


@app.route("/producto/save", methods = ["POST"])
def prod_save():
    frm = Productos()
    nombre = frm.nombre.data
    precio = frm.precio.data
    stock = frm.stock.data
    if len(nombre) > 0:
        if len(precio) > 0:
            if len(stock) > 0:
                with sqlite3.connect("vacunacion.db") as con:
                    cur = con.cursor()
                    cur.execute("INSERT INTO productos (nombre,precio,stock) VALUES (?,?,?)", [
                                nombre, precio, stock])
                    con.commit()
                    flash("Guardado con éxito")
            else:
                flash("ERROR: Stock es requerido")
        else:
            flash("ERROR: Precio es requerido")
    else:
        flash("ERROR: Nombre es requerido")

    return render("productos.html", frm=frm)
#dfsdfsd
@app.route("/producto/get",methods=["POST"])
def prod_get():
    frm=Productos()
    codigo=frm.codigo.data
    if len(codigo)>0:
        with sqlite3.connect("vacunacion.db") as con:
            con.row_factory=sqlite3.Row #lista de diccionario
            cur = con.cursor()
            cur.execute("SELECT * from productos WHERE codigo=?",[codigo])
            row=cur.fetchone()
            if row:
                frm.nombre.data =row["nombre"]
                frm.precio.data =row["precio"]
                frm.stock.data =row["stock"]
            else:
                frm.nombre.data = ""
                frm.precio.data = ""
                frm.stock.data = ""
                flash("Producto No encontrado")
    #return f"{row}"
    return render("productos.html",frm=frm)

@app.route("/producto/delete", methods=["POST"])
def prod_delete():
    frm = Productos()
    codigo = escape(frm.codigo.data)
    if codigo:
        with sqlite3.connect("vacunacion.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM productos WHERE codigo = ?", [codigo])
            con.commit()
            if con.total_changes > 0:
                flash("Producto Eliminado")
            else:
                flash("Producto NO se pudo eliminar")

    return render("productos.html", frm=frm)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__=="__main__":
    app.run(debug=True)