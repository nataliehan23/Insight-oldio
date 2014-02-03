var fileslist = []
var titlelist = []
var i = 0
var viewheight

function load_more_posters(){
    for(var j=i; j<i+5; j++){
            $('#posterlist').append("<a href='/search?musictitle="+titlelist[j]+"'>"+
                // "<img src="+fileslist[j]+" class='movieposter' width="'230'" height="'300'">"+
                "<img src="+fileslist[j]+" class='movieposter' width=20% height=200>"+
                // "<img src="+fileslist[j]+" class='movieposter' width=20%>"+
                "</a>"
            )    }
    i += 5
}


$.ajax({
    dataType: "json",
    url: 'static/json/CDImageLists_seed.json',
    success: function(result){
        viewheight = $(window).height()

        for(var j=0; j<result.length; j++){
            titlelist.push(result[j][0])
            fileslist.push(result[j][1])
        }
        // fileslist = result;
        $(window).scroll(function() {
           if($(window).scrollTop() + viewheight >= $(document).height()) {
              load_more_posters()
            }
        })
        for(var j=0; j<5; j++){
            link = "\"/search?musictitle=";
            link = link.concat(titlelist[j])
            $('#posterlist').append("<a href="+link+"\">"+
                "<img src="+fileslist[j]+" class='movieposter' width=20% height=200 class='posimg'>"+
                "</a>"
            )
        }
        i += 5
    }
});