(function ($) {
    $.fn.languageSelector = function (options) {
        var settings = $.extend({}, options);
        return this.each(function () {
            var $input = $(this);
            $input.select2({
              placeholder: "Search for a language...",
              minimumInputLength: 2,
              ajax: {
                url: $input.data("source-url"),
                dataType: "json",
                quietMillis: 250,
                data: function (term, page) {
                  return {q: term}
                },
                results: function (data, page) {
                  console.log(data.results);
                  return {results: data.results}
                },
                cache: true
              },
              initSelection: function (element, callback) {
                data = {
                  "pk": element.data("lang-pk"),
                  "ln": element.data("lang-ln"),
                  "lc": element.data("lang-lc"),
                  "lr": element.data("lang-lr")
                }
                callback(data);
              },
              id: function (lang) { return lang.pk; },
              formatResult: function (lang) {
                return "<strong>" + lang.ln + "</strong> <code>" + lang.lc + "</code> [" + lang.lr + "]";
              },
              formatSelection: function (lang) {
                return "<strong>" + lang.ln + "</strong> <code>" + lang.lc + "</code> [" + lang.lr + "]";
              },
              escapeMarkup: function (m) { return m; }
            });
        });
    }
})(jQuery);

$(function () {
    $("table[data-source]").each(function () {
        var $el = $(this);
        $el.DataTable({
            serverSide: true,
            ajax: $el.data("source"),
            stateSave: true
        });
    });
    $(".select2-multiple").select2();
    $(".language-selector").languageSelector();
    $(".date-picker").daterangepicker({
      singleDatePicker: true
    });
    $(document).on("eldarion-ajax:success", function (evt, $el) {
        if ($el.hasClass("navbar-form")) {
            var $el = $("<div>")
              .addClass("alert")
              .addClass("alert-info")
              .html("<strong>Invite was sent!</sent>");
            $("body").prepend($el);
            setTimeout(function(){ $el.remove(); }, 3000);
        }
    });
});
