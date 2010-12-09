var isMouseovered;
var inAnimation;

$(document).ready(function(){
	setWidth();
	var attachCnt=1;
	
	// 풀스크린 사용을 위한 전체 너비 조정	
	$("#linksModalBG").css("opacity",0.75).css("height",$(document).height());
	
	$("#linksModalBG").hide();
	$("#linksModal").hide();
	
	$("#topLinks #moreLinks").bind("click",function(){
		$("#linksModal").fadeIn();
		$("#linksModalBG").fadeIn();
	});
	$("#linksModal .quitModal").click(function(){
		$("#linksModal").fadeOut("fast");
		$("#linksModalBG").fadeOut("fast");
	});

    // 화면 크기 변경시 화면 재구성
    $(document).resize(setWidth);
	
	/* 메뉴 롤오버 js */
    inAnimation = false;
    $(".category").click( function(event){
        if(inAnimation) return;
        if($(this).is(".selected")) $(this).removeClass("selected");
        else { $(".category").removeClass("selected"); $(this).addClass("selected"); }
        toggleCat($(this).attr("rel"));
        event.preventDefault();
    });
		
//	$(".selectObject a")
//		.bind("click", function() { $(this).toggleClass("selected"); });
		
	$(".dropBox a")
		.bind("click", function(){
			$("~ul",this).toggle();
			$(this).toggleClass("opened");
			// checkbox를 hide해서 jQuery로 data만 연동하세요
		});
	$(".dropBox ul a")
		.bind("click", function(){
			$(this).parent().parent().parent().children("a").text($(this).text());
			$(this).parent().parent().parent().children("a").toggleClass("opened");
			$(this).parent().parent().hide();
			// select-option을 hide해서 jQuery로 data만 연동하세요
		});
		
	if($.browser.msie && $.browser.version=="6.0") {
		setTimeout("upgradeBrowser()",1000);
		$(window).bind("scroll",browserOnTop);
	}
	if ($("#araId").length) $("#araId").focus();


        // English 클릭시 팝업
        $(".menuRight .fr").eq(1).children().click( function(event){
                alert("We're sorry. Under construction ...");
                });
});

function setWidth () {
	// 윈도우 리사이즈시 전체 너비 / 첨부파일 리사이징.
	var contentsWidth = $(window).width()-160;
	if(contentsWidth<830) contentsWidth=830; // 최소 너비 규정
	
	$("#mainWrap").css("width",contentsWidth+160); // IE6은 min-width가 안먹어요 ㅠㅠ
	$("#navigation").css("width",contentsWidth+160); // IE6은 min-width가 안먹어요 ㅠㅠ
	$("#topLinks").css("width",contentsWidth+140);
	$("#contents").css("width",contentsWidth);
	setCategoryListWidth("#boardInCategory dl:visible ul");
	$(".mainBody .mainNotice .mainItemContents").css("width",contentsWidth-111);
	$(".mainBody .mainNotice .mainItemContents #mainBanner .bannerDesc").css("width",contentsWidth-696);
	$(".mainBody .mainItem .mainItemContents").css("width",contentsWidth-110);
	
	$(".writeTable .writeContents textarea").css("width",contentsWidth-60);
	$(".articleView .attached td div").css("width",contentsWidth-107);

	$(".replyBox .attached td div").each(function(){
            var depth = $(this).parents(".replyBox").length;
            $(this).css("width",contentsWidth-(107+35*depth));
        });}

/* 메뉴 롤오버에 쓰이는 js */
function toggleCat (catName) {
	var entireHandler = "#boardIn" + catName;
    if(isMouseovered){
        if($(entireHandler).is(":hidden")){
            $("#boardInCategory dl.boardList").hide();
            $(entireHandler).show();
        } else {
            callHideCat();
        }
    } else {
        isMouseovered=1;
        inAnimation = true;
        $(entireHandler).slideDown('fast', function() { inAnimation = false; });
    }
    setCategoryListWidth("#boardInCategory dl:visible ul");
}

function callHideCat () {
	isMouseovered=0;
    inAnimation = true;
	setTimeout("hideCat()",200);
}

function hideCat () {	
	if(!isMouseovered) {
		$("#noMenu #boardInCategory").slideUp('fast', function() { inAnimation = false; });
		$("#boardInCategory dl.boardList").slideUp('fast', function() { inAnimation = false; });
	}
}

function upgradeBrowser () {
	$("#upgradeBrowser").fadeIn(1000);
}

function browserOnTop() {
	$("#upgradeBrowser").css("top",$(window).scrollTop());
}

function setCategoryListWidth(handler) {
	var categoryWidth = $(window).width() - 160;
	var categoryNum = $(handler).length;
	if (categoryWidth < (categoryNum * 154 + 90)) categoryWidth = categoryNum * 154 + 90;
	$("#boardInCategory").css("width", categoryWidth); // boardInCategory의 min-width를 지정
}
