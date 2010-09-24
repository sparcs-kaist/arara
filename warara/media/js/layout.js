var isMouseovered;

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
	
	/* 메뉴 롤오버 js */
	$("#navigation .favorite")
		.bind("click", {catName:".favorite"}, showCat)
		.bind("mouseover", {catName:".favorite"}, showCat)
		.bind("mouseout", callHideCat);
	$("#navigation .category1")
		.bind("click", {catName:".category1"}, showCat)
		.bind("mouseover", {catName:".category1"}, showCat)
		.bind("mouseout", callHideCat);
	$("#navigation .category2")
		.bind("click", {catName:".category2"}, showCat)
		.bind("mouseover", {catName:".category2"}, showCat)
		.bind("mouseout", callHideCat);
	$("#navigation .category3")
		.bind("click", {catName:".category3"}, showCat)
		.bind("mouseover", {catName:".category3"}, showCat)
		.bind("mouseout", callHideCat);
	$("#navigation .category4")
		.bind("click", {catName:".category4"}, showCat)
		.bind("mouseover", {catName:".category4"}, showCat)
		.bind("mouseout", callHideCat);
	$("#navigation .category5")
		.bind("click", {catName:".category5"}, showCat)
		.bind("mouseover", {catName:".category5"}, showCat)
		.bind("mouseout", callHideCat);
		
	$("#boardInCategory dl")
		.bind("mouseover",function() { isMouseovered=1; })
		.bind("mouseout", callHideCat);
		
	$(".selectObject a")
		.bind("click", function() { $(this).toggleClass("selected"); });
		
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
});

function setWidth () {
	// 윈도우 리사이즈시 전체 너비 / 첨부파일 리사이징.
	var contentsWidth = $(window).width()-160;
	if(contentsWidth<830) contentsWidth=830; // 최소 너비 규정
	
	$("#mainWrap").css("width",contentsWidth+160); // IE6은 min-width가 안먹어요 ㅠㅠ
	$("#navigation").css("width",contentsWidth+160); // IE6은 min-width가 안먹어요 ㅠㅠ
	$("#contents").css("width",contentsWidth);
	$("#noMenu #boardInCategory").css("width",contentsWidth);
	$(".mainBody .mainNotice .mainItemContents").css("width",contentsWidth-111);
	$(".mainBody .mainNotice .mainItemContents #mainBanner .bannerDesc").css("width",contentsWidth-696);
	$(".mainBody .mainItem .mainItemContents").css("width",contentsWidth-110);
	
	$(".writeTable .writeContents textarea").css("width",contentsWidth-60);
	$(".articleView .attached td div").css("width",contentsWidth-107);
}

/* 메뉴 롤오버에 쓰이는 js */
function showCat (event) {
	$("#noMenu #boardInCategory").show();
	isMouseovered=1;
	var entireHandler = "#boardInCategory dl" + event.data.catName;
	$("#boardInCategory dl.favorite").hide();
	$("#boardInCategory dl.category1").hide();
	$("#boardInCategory dl.category2").hide();
	$("#boardInCategory dl.category3").hide();
	$("#boardInCategory dl.category4").hide();
	$("#boardInCategory dl.category5").hide();
	$(entireHandler).show();
}

function callHideCat () {
	isMouseovered=0;
	setTimeout("hideCat()",1000);
}

function hideCat () {	
	if(!isMouseovered) {
		$("#noMenu #boardInCategory").hide();
		$("#boardInCategory dl.favorite").hide();
		$("#boardInCategory dl.category1").hide();
		$("#boardInCategory dl.category2").hide();
		$("#boardInCategory dl.category3").hide();
		$("#boardInCategory dl.category4").hide();
		$("#boardInCategory dl.category5").hide();
		$("#favorite #contents .favorite").show();
		$("#category1 #contents .category1").show();
		$("#category2 #contents .category2").show();
		$("#category3 #contents .category3").show();
		$("#category4 #contents .category4").show();
		$("#category5 #contents .category5").show();
	}
}

function upgradeBrowser () {
	$("#upgradeBrowser").fadeIn(1000);
}

function browserOnTop() {
	$("#upgradeBrowser").css("top",$(window).scrollTop());
}