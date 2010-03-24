// adminpostwysiwyg.js
$(document).ready(function() {
	var options = {
            toolbar: [
                ['Bold','Italic','Underline','Strike','-','Subscript','Superscript'],
                ['NumberedList','BulletedList','-','Outdent','Indent','Blockquote'],
                ['JustifyLeft','JustifyCenter','JustifyRight','JustifyBlock'],
                ['Link','Unlink','Anchor'],
                ['Format','Font','FontSize'],
                ['TextColor','BGColor'],
                '/',
                ['Image','Flash','Table','HorizontalRule','Smiley','SpecialChar','PageBreak'],
                ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton', 'HiddenField'],
                ['Cut','Copy','Paste','PasteText','PasteFromWord','-','Print', 'SpellChecker', 'Scayt'],
                ['Undo','Redo','-','Find','Replace','-','SelectAll','RemoveFormat'],
                ['Maximize', 'ShowBlocks','-','About']
            ]
        };
	$("#id_content").ckeditor(function() { /* callback code */ }, options);
});

