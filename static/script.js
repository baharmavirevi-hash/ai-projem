window.addEventListener("load", function(){

    setTimeout(function(){

        const splash = document.getElementById("splash-screen");

        if(splash){

            splash.style.opacity = "0";

            setTimeout(function(){

                splash.style.display = "none";

            },600);

        }

    },2000);

});
