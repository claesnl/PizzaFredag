$(function() {
	$('#numguests').hide();
	$('#numguests_label').hide();
	 
    $('#persons1').parent().click(function(){
		$('#numguests').hide();
		$('#numguests_label').hide();
	});
	$('#personsx').parent().click(function(){
		$('#numguests').hide();
		$('#numguests_label').hide();
	});
	
	$('#persons2').parent().click(function(){
		$('#numguests').show();
		$('#numguests_label').show();
	});
	
	$('.remove').click(function(){
		if(!confirm('Are you sure?')){
			return false;
		}
	});
	
});

