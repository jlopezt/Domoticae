const FONDO     ="#DDDDDD";
const TEXTO     ="#000000";
const ACTIVO    ="#FFFF00";
const DESACTIVO ="#DDDDDD";

function inicializaDiv() {
    var xhServicios = new XMLHttpRequest();
    xhServicios.onreadystatechange = function() {
        if (xhServicios.readyState == 4) {
        if(xhServicios.status == 200) {
            console.log("JSON: " + xhServicios.responseText)
            var res = JSON.parse(xhServicios.responseText);

            var servicios=res.datos;//Servicios;

            servicios.forEach(function(servicio,indice) {
                if (typeof servicio !== 'undefined'){
                    switch(servicio){
                        case "Entradas":
                            var xhEntradas = new XMLHttpRequest();
                            xhEntradas.onreadystatechange = function(){
                                if (xhEntradas.readyState == 4){
                                    if(xhEntradas.status == 200) {
                                    console.log("JSON: " + xhEntradas.responseText)
                                    actualizaEntradas(xhEntradas.responseText);
                                    }
                                }
                            };
                            xhEntradas.open("GET","http://{{ SID }}/estadoEntradas", true);
                            xhEntradas.send(null);                     
                            break;
                        case "Variables":
                            var xhVariables = new XMLHttpRequest();
                            xhVariables.onreadystatechange = function(){
                                if (xhVariables.readyState == 4){
                                    if(xhVariables.status == 200) {
                                    console.log("JSON: " + xhVariables.responseText)
                                    actualizaVariables(xhVariables.responseText);
                                    }
                                }
                            };
                            xhVariables.open("GET","http://{{ SID }}/estadoVariables", true);
                            xhVariables.send(null); 
                            break;
                        case "Salidas":
                            var xhSalidas = new XMLHttpRequest();
                            xhSalidas.onreadystatechange = function(){
                                if (xhSalidas.readyState == 4){
                                    if(xhSalidas.status == 200) {
                                    console.log("JSON: " + xhSalidas.responseText)
                                    actualizaSalidas(xhSalidas.responseText);
                                    }
                                }
                            };
                            xhSalidas.open("GET", "http://{{ SID }}/estadoSalidas", true);
                            xhSalidas.send(null);                     
                            break;
                        case "Secuenciador":
                            var xhSecuenciador = new XMLHttpRequest();
                            xhSecuenciador.onreadystatechange = function(){
                                if (xhSecuenciador.readyState == 4){
                                    if(xhSecuenciador.status == 200) {
                                    console.log("JSON: " + xhSecuenciador.responseText)
                                    actualizaSecuenciador(xhSecuenciador.responseText);
                                    }
                                }
                            };
                            xhSecuenciador.open("GET", "http://{{ SID }}/estadoSecuenciador", true);
                            xhSecuenciador.send(null); 
                            break;
                        case "MaquinaEstados":
                            var xhME = new XMLHttpRequest();
                            xhME.onreadystatechange = function(){
                                if (xhME.readyState == 4){
                                    if(xhME.status == 200) {
                                    console.log("JSON: " + xhME.responseText)
                                    actualizaMaquinaEstados(xhME.responseText);
                                    }
                                }
                            };
                            xhME.open("GET", "http://{{ SID }}/estadoMaquinaEstados", true);
                            xhME.send(null); 
                            break;
                        case "Imagen":
                            break;
                        }
                    }
                });
            }
        }
    };
    xhServicios.open("GET", "http://{{ SID }}/servicios", true);
    xhServicios.send(null);  

    //Conecta por MQTT con el dispositivo
    //connect();
}

function actualizaVariables(datos) {
    var res = JSON.parse(datos);

    //variables
    var variables=res.datos;//Variables;
    console.log("numero variables: " + variables.length);

    if(variables.length==0) return;//Si no hay variables salgo
    var div=document.getElementById("div_variables");
    div.setAttribute("class","margen visible");

    variables.forEach(function(variable,indice,array) {
        var hilera = document.getElementById("variable_"+indice);
        if(hilera==null){
            console.log("no existe la fila, la creo");
            var hilera = document.createElement("tr");
            hilera.setAttribute("id", "variable_" + indice);
            hilera.setAttribute("class","modo2");
            document.getElementById("body_tabla_variables").appendChild(hilera);

            var celda = document.createElement("td");
            celda.setAttribute("id","variable_id_"+indice);
            celda.setAttribute("align","right");
            hilera.appendChild(celda);

            celda = document.createElement("td");
            celda.setAttribute("id","variable_nombre_"+indice);
            celda.setAttribute("align","right");
            hilera.appendChild(celda);

            celda = document.createElement("td");
            celda.setAttribute("id","variable_valor_"+indice);
            celda.setAttribute("align","center");
            hilera.appendChild(celda);

            celda = document.createElement("td");
            celda.setAttribute("id","variable_unidades_"+indice);
            celda.setAttribute("align","center");
            hilera.appendChild(celda);
        }

        document.getElementById("variable_id_" + indice).innerHTML=indice;//variable.id;
        document.getElementById("variable_nombre_" + indice).innerHTML=variable.nombre;
        document.getElementById("variable_valor_" + indice).innerHTML=variable.valor;
        document.getElementById("variable_unidades_" + indice).innerHTML=variable.unidades;
        //let cad="";
        //for (const x in variable) {
        //    console.log('analizo x= ' + x + ' | valor: ' + variable[x]);
        //    if(x!='nombre') cad += x + ' = ' + variable[x] + '<BR>';            
        //}
        //document.getElementById("variable_valor_" + indice).innerHTML=cad;
    });

    //Si hay filas de mas, las borro
    var tabla = document.getElementById("tabla_variables");
    if(tabla.rows.length-1>variables.length){ //si hay mas filas que habitaciones, le resto la cabecera
        console.log("filas en tabla: " + (tabla.rows.length-1) + " | variables: " + variables.length);
        for(i=tabla.rows.length;i>variables.length+1;i--){
            console.log("borro la fila " + (i));
            tabla.deleteRow(i-1);
        }
    }
}

function actualizaEntradas(datos) {
    var res = JSON.parse(datos);

    //entradas
    var entradas=res.datos;//entradas;
    console.log("numero entradas: " + entradas.length);

    if(entradas.length==0) return;//Si no hay medidas salgo
    var div=document.getElementById("div_entradas");
    div.setAttribute("class","margen visible");

    entradas.forEach(function(entrada,indice,array) {
        var hilera = document.getElementById("entrada_"+indice);
        if(hilera==null){
            console.log("no existe la fila, la creo");
            var hilera = document.createElement("tr");
            hilera.setAttribute("id", "entrada_" + indice);
            hilera.setAttribute("class","modo2");
            document.getElementById("body_tabla_entradas").appendChild(hilera);

            var celda = document.createElement("td");
            celda.setAttribute("id","entrada_id_"+indice);
            celda.setAttribute("align","right");
            hilera.appendChild(celda);

            celda = document.createElement("td");
            celda.setAttribute("id","entrada_nombre_"+indice);
            celda.setAttribute("align","right");
            hilera.appendChild(celda);

            celda = document.createElement("td");
            celda.setAttribute("id","entrada_estado_"+indice);
            celda.setAttribute("align","center");
            hilera.appendChild(celda);
        }

        document.getElementById("entrada_id_" + indice).innerHTML=entrada.id;
        document.getElementById("entrada_nombre_" + indice).innerHTML=entrada.nombre;
        document.getElementById("entrada_estado_" + indice).innerHTML=(entrada.estado==0?"Off":"On");
    });

    //Si hay filas de mas, las borro
    var tabla = document.getElementById("tabla_entradas");
    if(tabla.rows.length-1>entradas.length){ //si hay mas filas que habitaciones, le resto la cabecera
        console.log("filas en tabla: " + (tabla.rows.length-1) + " | entradas: " + entradas.length);
        for(i=tabla.rows.length;i>entradas.length+1;i--){
            console.log("borro la fila " + (i));
            tabla.deleteRow(i-1);
        }
    }
}

function actualizaSalidas(datos) {
    var res = JSON.parse(datos);

    //salidas
    var salidas=res.datos;//salidas;
    console.log("numero salidas: " + salidas.length);

    if(salidas.length==0) return;//Si no hay medidas salgo
    var div=document.getElementById("div_salidas");
    div.setAttribute("class","margen visible");

    salidas.forEach(function(salida,indice,array) {
        var hilera = document.getElementById("salida_"+indice);
        if(hilera==null){
            console.log("no existe la fila, la creo");
            var hilera = document.createElement("tr");
            hilera.setAttribute("id", "salida_" + indice);
            hilera.setAttribute("class","modo2");
            document.getElementById("body_tabla_salidas").appendChild(hilera);

            var celda = document.createElement("td");
            celda.setAttribute("id","salida_id_"+indice);
            celda.setAttribute("align","right");
            hilera.appendChild(celda);

            celda = document.createElement("td");
            celda.setAttribute("id","salida_nombre_"+indice);
            celda.setAttribute("align","right");
            hilera.appendChild(celda);

            celda = document.createElement("td");
            celda.setAttribute("id","salida_estado_"+indice);
            celda.setAttribute("align","center");
            hilera.appendChild(celda);

            celda = document.createElement("td");
            celda.setAttribute("id","salida_modo_"+indice);
            celda.setAttribute("align","center");
            hilera.appendChild(celda);

            celda = document.createElement("td");
            celda.setAttribute("id","salida_accion_"+indice);
            celda.setAttribute("align","center");
            hilera.appendChild(celda);
        }

        document.getElementById("salida_id_" + indice).innerHTML=salida.id;
        document.getElementById("salida_nombre_" + indice).innerHTML=salida.nombre;
        
        //document.getElementById("salida_estado_" + indice).innerHTML=salida.nombreEstado;
        var estado=document.getElementById("salida_estado_" + indice);
        estado.innerHTML=salida.nombreEstado;

        document.getElementById("salida_modo_" + indice).innerHTML=salida.modo;

        var accion=document.getElementById("salida_accion_" + indice);

        //accion.innerHTML="<p>Modo " + salida.modo + "</p>";
        if(salida.modo=="Manual" || salida.modo=="Secuenciador"){
            if(salida.estado==0) {
                estado.style.backgroundColor=DESACTIVO;

                //accion.innerHTML  = "<form action='activaSalida'><input  type='hidden' id='activa_" + indice + "' name='id' value='" + indice + "'><input STYLE='color: #000000; text-align: center; background-color: #FFFF00; width: 80px' type='submit' value='activar'></form>";
                accion.innerHTML  += "<input STYLE='color: #000000; text-align: center; background-color: #FFFF00; width: 80px' type='button' value='activar' onclick='actuaSalida(\"" + salida.id + "\",\"activaSalida\")' onMouseOver='this.style.cursor=\"pointer\"'>";
                //accion.innerHTML += "<form action='pulsoSalida'><input  type='hidden' id='pulso_" + indice + "' name='id' value='" + indice + "'><input STYLE='color: #000000; text-align: center; background-color: #FFFF00; width: 80px' type='submit' value='pulso'></form>";
                accion.innerHTML  += "<input STYLE='color: #000000; text-align: center; background-color: #FFFF00; width: 80px' type='button' value='pulso' onclick='actuaSalida(\"" + salida.id + "\",\"pulsoSalida\")' onMouseOver='this.style.cursor=\"pointer\"'>";
            }
            else {
                estado.style.backgroundColor=ACTIVO;
                
                //accion.innerHTML  = "<form action='desactivaSalida'><input  type='hidden' id='desactiva_" + indice + "' name='id' value='" + indice + "'><input STYLE='color: #000000; text-align: center; background-color: #DDDDDD; width: 80px' type='submit' value='desactivar'></form>";
                accion.innerHTML  += "<input STYLE='color: #000000; text-align: center; background-color: #DDDDDD; width: 80px' type='button' value='desactivar' onclick='actuaSalida(\"" + salida.id + "\",\"desactivaSalida\")'>";
            }
        }
        else{
            //accion.innerHTML="<p>Modo " + salida.modo + "</p>";
            accion.innerHTML=" -- ";
        }
    });

    //Si hay filas de mas, las borro
    var tabla = document.getElementById("tabla_salidas");
    if(tabla.rows.length-1>salidas.length){ //si hay mas filas que salidas, le resto la cabecera
        console.log("filas en tabla: " + (tabla.rows.length-1) + " | salidas: " + salidas.length);
        for(i=tabla.rows.length;i>salidas.length+1;i--){
            console.log("borro la fila " + (i));
            tabla.deleteRow(i-1);
        }
    }
}

function actualizaSecuenciador(datos) {
    var res = JSON.parse(datos);

    //Secuenciador
    var planes=res.datos;//planes;
    console.log("numero planes: " + planes.length);

    if(planes.length==0) return;//Si no hay medidas salgo
    var div=document.getElementById("div_secuenciador");
    div.setAttribute("class","margen visible");
    
    //Boton de activacion/desactivacion
    if(res.estado==0){
        //document.getElementById("secuenciadorCaption").innerHTML  = "Secuenciadores <form action='activaSecuenciador'><input STYLE='color: #000000; text-align: center; background-color: #FFFF00; width: 80px' type='submit' value='activar'></form>";
        document.getElementById("secuenciadorCaption").innerHTML  = "Secuenciadores <input STYLE='color: #000000; text-align: center; background-color: #FFFF00; width: 80px' type='buttom' value='activar' onclick='actuaSecuenciador(\"activaSecuenciador\")'  onMouseOver='this.style.cursor=\"pointer\"'>";
    }
    else{
        //document.getElementById("secuenciadorCaption").innerHTML  = "Secuenciadores <form action='desactivaSecuenciador'><input STYLE='color: #000000; text-align: center; background-color: #DDDDDD; width: 80px' type='submit' value='desactivar'></form>";
        document.getElementById("secuenciadorCaption").innerHTML  = "Secuenciadores <input STYLE='color: #000000; text-align: center; background-color: #DDDDDD; width: 80px' type='button' value='desactivar' onclick='actuaSecuenciador(\"desactivaSecuenciador\")' onMouseOver='this.style.cursor=\"pointer\"'>";
    }

    planes.forEach(function(plan,indice,array) {
        var hilera = document.getElementById("plan_"+indice);
        if(hilera==null){
            console.log("no existe la fila, la creo");
            var hilera = document.createElement("tr");
            hilera.setAttribute("id", "plan_" + indice);
            hilera.setAttribute("class","modo2");
            document.getElementById("body_tabla_secuenciador").appendChild(hilera);

            var celda = document.createElement("td");
            celda.setAttribute("id","plan_id_"+indice);
            celda.setAttribute("align","right");
            hilera.appendChild(celda);

            celda = document.createElement("td");
            celda.setAttribute("id","plan_nombre_"+indice);
            celda.setAttribute("align","right");
            hilera.appendChild(celda);

            celda = document.createElement("td");
            celda.setAttribute("id","plan_salida_"+indice);
            celda.setAttribute("align","center");
            hilera.appendChild(celda);

            celda = document.createElement("td");
            celda.setAttribute("id","plan_estado_"+indice);
            celda.setAttribute("align","center");
            hilera.appendChild(celda);
        }

        document.getElementById("plan_id_" + indice).innerHTML=plan.id;
        document.getElementById("plan_nombre_" + indice).innerHTML=plan.nombre;
        document.getElementById("plan_salida_" + indice).innerHTML=plan.salida;                
        document.getElementById("plan_estado_" + indice).innerHTML=plan.estado;
    });
}

function actualizaMaquinaEstados(datos) {

    if(datos=="{}") return;//Si no hay medidas salgo
    var div=document.getElementById("div_maquinaEstados");
    div.setAttribute("class","margen visible");

    var res = JSON.parse(datos);

    //salidas
    var estado=res.estado;
    console.log("estado: " + estado);
    document.getElementById("estadoME").innerHTML=estado;
}

function actuaSalida(salida,accion){
    console.log('Accion: ' + accion + ' | Salida ' + salida)

    var acciones = {'activaSalida':1,'desactivaSalida':2,'pulsoSalida':3,'fuerzaSalidaManual':4,'recuperaSalidaManual':5};
    if(!(accion in acciones)) return false;

    var xhCambia = new XMLHttpRequest();
    xhCambia.onreadystatechange = function(){
        if (xhCambia.readyState == 4){
            if(xhCambia.status != 200) {
              alert('Error en la accion: ' + xhCambia.responseText);
            }
            else console.log("ejecutado con exito");
            location.reload();
          }
      };
    xhCambia.open("POST", "http://{{ SID }}/" + accion + "?id=" + salida, true);
    xhCambia.send(null);          
  };    

  function actuaSecuenciador(accion){
    console.log('Accion: ' + accion);

    var acciones = {'activaSecuenciador':1,'desactivaSecuenciador':2};
    if(!(accion in acciones)) return false;    

    var xhCambia = new XMLHttpRequest();
    xhCambia.onreadystatechange = function(){
        if (xhCambia.readyState == 4){
            if(xhCambia.status != 200) {
              alert('Error: ' + xhCambia.responseText);
            }
            else console.log("ejecutado con exito");
            location.reload();
          }
      };
    xhCambia.open("POST", "http://{{ SID }}/" + accion, true);
    xhCambia.send(null);          
  };      
