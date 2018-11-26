$(document).ready(function() {
	$("#review-form").submit(function(event) {
		if ($("#rating").val() === '0') {
			$("#rating-error").html("You must submit a rating from 1 to 5")
			event.preventDefault()
		}
		if (!$.trim($("#text").val())) {
			$("#review-error").html("You must submit a review to give a rating")
			event.preventDefault()
		}
	})

	$(".rating-star").on('click', function() {
		$("#rating").val(this.alt)
		highlightStars(this)
	})

	$(".rating-star").hover(function() {
		if ($("#rating").val() === '0') {
			highlightStars(this)
		}
	}, function() {
		if ($("#rating").val() === '0') {
			unhighlightStars()
		}
	})	
})

function highlightStars(star) {
	let id = "#" + star.id
	starGold(id)
	for (let i = parseInt(star.alt)-1; i > 0; i--) {	
		let alt = i.toString()			
		let newStar = `img[alt=${alt}]`
		starGold($(newStar))
	}
	for (let j = parseInt(star.alt)+1; j < 6; j++) {
		let alt = j.toString()
		let newStar = `img[alt=${alt}]`
		starOutline($(newStar))
	}
}

function unhighlightStars() {
	$(".rating-star").attr("src", "static/outline_star.png")
}
 
function starGold(star) {
	$(star).attr("src", "static/gold_star.png")
}

function starOutline(star) {
	$(star).attr("src", "static/outline_star.png")
}