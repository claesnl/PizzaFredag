$(function() {
	$('#numguests').hide();
	 
    $('#persons1').click(function(){
		$('#numguests').hide();
	});
	$('#personsx').click(function(){
		$('#numguests').hide();
	});
	
	$('#persons2').click(function(){
		$('#numguests').show();
	});
	
	$('.remove').click(function(){
		if(!confirm('Are you sure?')){
			return false;
		}
	});
});