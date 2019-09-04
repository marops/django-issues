from django.forms.widgets import SelectMultiple

class SelectMultipleTag(SelectMultiple):

    class Media:
        css = {
            'all': ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.10/css/select2.min.css",)
        }
        js = ("https://cdnjs.cloudflare.com/ajax/libs/select2/4.0.10/js/select2.min.js",'js/select2_tags.js')