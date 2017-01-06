/**
 * Configures application.
 */
function configure()
{

    // configure typeahead
    $("#q").typeahead({
        highlight: false,
        minLength: 1
    },
    {
        display: function(suggestion) { return suggestion.Player; },
        limit: 10,
        source: find,
        templates: {
            suggestion: Handlebars.compile(
                "<div class='autocomplete_box'>" +
                "{{ Player }}" +
                "</div>"
            )
        }
    });
}    

function find(query, syncResults, asyncResults)
{
    // get players matching query (asynchronously)
    var parameters = {
        q: query
    };
    $.getJSON(Flask.url_for("find"), parameters)
    .done(function(data, textStatus, jqXHR) {
     
        // call typeahead's callback with find results (i.e., player names )
        asyncResults(data);
    })
    .fail(function(jqXHR, textStatus, errorThrown) {

        // log error to browser's console
        console.log(errorThrown.toString());

        // call typeahead's callback with no results
        asyncResults([]);
    });
}

//run the configure function when the page is ready to go
$(document).ready(configure);