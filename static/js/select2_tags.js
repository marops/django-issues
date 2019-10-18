$(document).ready(function(){
    //===== Select2 =====
    // This adds Select2 interface to add/edit tags which is a Taggit TaggableMager formfield

    //tags_all must be passed to the template from the view

    //hide the Taggit.TaggableManager fromfield
    $('#id_tags').attr({"type":"hidden"})

    //tags_all must be passed by the view to the tmplate

    $('#id_tags_select').select2({
      tags: true,
      placeholder: "Select or enter a Tag",
      data: data,
      tokenSeparators: [',']
    });

    //This pulls tags from the comma delimited string from fieldname tags
//    t=$("#id_tags").val()
//    arr=t.split(",")
    arr=$("#id_tags").val().trim().split(/\s*,\s*/);
    //console.log(arr)
    //taggit puts " around string with space which needs to be removed for Select2. Just neec comma delimited
    for(i in arr){
        arr[i]=arr[i].replace(/\"/gm, "");
        //console.log(arr[i])
    }
    $('#id_tags_select').val(arr);
    $('#id_tags_select').trigger('change');

    //on submit, puts selected tags from tag select into fieldname tags
    $("form").submit(function(){
        tags=$("#id_tags_select").val()
        $("#id_tags").val(tags)
    });
})