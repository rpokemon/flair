
flair.sheet_filter = null;
flair.sheet_filter_change = false;
flair.typing_timeout = null;


flair.updateRegionFilter = function (sheet_name) {
    if (sheet_name == 'ALL') {
        flair.sheet_filter = null;
    } else {
        flair.sheet_filter = sheet_name;
    }

    flair.sheet_filter_change = true;
    flair.updateFilter();
}

flair.updateFilter = function (text) {
    text = text || document.getElementById('flair-filter-text').value;

    var is_int = text >>> 0 === parseFloat(text);
    if (is_int) {
        text = text.toString();
    }

    text = text.toLowerCase();

    for (var poke_id in flair.by_id) {
        if (flair.by_id.hasOwnProperty(poke_id)) {
            var poke_name = flair.by_id[poke_id].poke_name.toLowerCase();
            var sheet = flair.by_id[poke_id].sheet;

            var el = document.querySelector('.flair-choice[data-id="' + poke_id + '"]');
            if (el == null)
                continue;

            if (
                // check poke_name
                (text.length == 0 || text == poke_name || (poke_name.indexOf(text) !== -1 && isNaN(text)) ||
                    // check poke_id
                    text === poke_id || text === flair.by_id[poke_id].orig_id) &&
                // check sheet
                (flair.sheet_filter === null || flair.sheet_filter === sheet)
            ) {
                n.show(el);
            } else {
                n.hide(el);
            }
        }
    }

    var fn_hashUpdate = function () {
        var hash = "#";

        if (text.length != 0) {
            hash += "q=" + encodeURIComponent(text);
        }

        if (flair.sheet_filter != null) {
            if (hash.length != 1) {
                hash += "&";
            }

            hash += "r=" + encodeURIComponent(flair.sheet_filter);
        }

        history.replaceState(undefined, undefined, hash);
    };

    // sheet filter change should be an immediate hash change
    // for the text filter, we should wait for the user to be done typing
    if (flair.sheet_filter_change) {
        flair.sheet_filter_change = false;
        fn_hashUpdate();
    } else {
        if (flair.typing_timeout) {
            clearTimeout(flair.typing_timeout);
        }

        flair.typing_timeout = setTimeout(fn_hashUpdate, 600);
    }

}

flair.validate = function () {
    var flair_class = encodeURIComponent(document.getElementById('flair-selection-class').value);
    if (flair_class.length == 0) {
        alert('Choose a flair first!');
        return false;
    }

    var flair_text = encodeURIComponent(document.getElementById('flair-selection-text').value);
    if (flair_text.length == 0) {
        flair_text = '%0A';
    }
    if (flair_text.length > 64) {
        return false;
    }

    return true;
}

flair.selectChoice = function (poke_id, key) {
    var el = document.querySelector('.flair-choice[data-id="' + poke_id + '"]');

    if (!el) {
        return;
    }

    // If trainerflair disable subreddit selection checkbox
    var sr_choices = document.getElementsByClassName("sr-choice");
    if (el.getAttribute('class').indexOf("trainerflair") >= 0) {
        for (var i = 1; i < sr_choices.length; i++) {
            var input_el = sr_choices[i].firstChild;

            // If checkbox was selected save status
            if (input_el.checked) {
                input_el.waschecked = true;
            }

            input_el.checked = false;
            input_el.disabled = true;
        }
    } else {
        for (var i = 1; i < sr_choices.length; i++) {
            var input_el = sr_choices[i].firstChild;

            if (input_el.waschecked) {
                input_el.checked = true;
                input_el.waschecked = false;
            }

            input_el.disabled = false;
        }
    }

    n.removeClass(document.querySelectorAll('.flair-choice'), 'selected');
    n.addClass(el, 'selected');

    document.getElementById('flair-selection-class').value = key;
    document.getElementById('flair-selection-flair').setAttribute('class', 'flair ' + flair.by_id[poke_id].flair_class);
}

flair.loadChoices = function () {
    flair.load__by_id();

    var do_initial_updateFilter = false;

    if (window.location.hash) {
        var hash = window.location.hash.substring(1);

        if (hash == 'flair') {
            history.replaceState(undefined, undefined, "#");
        }

        var q = n.getParameterByName('q', "?" + hash);
        var r = n.getParameterByName('r', "?" + hash);

        if (q) {
            document.getElementById('flair-filter-text').value = q;
        }
        if (r) {
            var isAvailable = false;
            for (var i = 0; i < document.getElementById("flair-filter-sheet").length; i++) {
                if (document.getElementById("flair-filter-sheet").options[i].value == r) {
                    isAvailable = true;
                }
            }

            if (isAvailable) {
                document.getElementById('flair-filter-sheet').value = r;
                flair.sheet_filter = r;
            }
        }

        if (q || r) {
            do_initial_updateFilter = true;
        }
    }

    var enter = document.getElementById('flair-choices');
    for (var poke_id in flair.by_id) {
        if (flair.by_id.hasOwnProperty(poke_id)) {
            var data = flair.by_id[poke_id];

            var flair_choice = document.createElement('span');
            flair_choice.setAttribute('class', 'flair flair-choice ' + data.flair_class);
            flair_choice.setAttribute('data-name', data.poke_name);
            flair_choice.setAttribute('title', '#' + data.poke_id + ' ' + data.poke_name);
            flair_choice.setAttribute('data-id', data.poke_id);
            flair_choice.setAttribute('onclick', 'flair.selectChoice("' + data.poke_id + '","' + data.key + '")');

            enter.appendChild(flair_choice);
        }
    }

    var sr_enter = document.getElementById('subreddit-selection');
    for (var i = 0; i < flair.subreddits.length; i++) {
        var sr = flair.subreddits[i];

        var sr_choice = document.createElement('label');
        sr_choice.setAttribute('class', 'sr-choice');
        sr_choice.setAttribute('data-name', sr);
        sr_choice.setAttribute('for', 'sr-choice-' + sr);

        var sr_choice_input = document.createElement('input');
        sr_choice_input.setAttribute('id', 'sr-choice-' + sr);
        sr_choice_input.setAttribute('type', 'checkbox');
        sr_choice_input.setAttribute('checked', '');
        sr_choice_input.setAttribute('value', sr);
        sr_choice_input.setAttribute('name', 'subreddits[]')

        var sr_choice_span = document.createElement('span');
        sr_choice_span.textContent = sr;

        sr_choice.appendChild(sr_choice_input);
        sr_choice.appendChild(sr_choice_span);

        sr_enter.appendChild(sr_choice);

        if (i != flair.subreddits.length - 1) {
            var sr_sep = document.createElement('span');
            sr_sep.setAttribute('class', 'sr-sep');
            sr_sep.textContent = '|';
            sr_enter.appendChild(sr_sep);
        }
    }

    if (do_initial_updateFilter) {
        flair.updateFilter();
    }
}

document.addEventListener('DOMContentLoaded', flair.loadChoices, false);

/* UTILITIES
--------------------------------------------------------------------------------*/
var n = {};

n.getParameterByName = function (name, url) {
    var match = RegExp('[?&]' + name + '=([^&]*)').exec(url);
    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
}

n.addClass = function (o, className) {
    if (!o || !className || !className.length)
        return;

    o = n.isString(o) ? document.querySelectorAll(o) : o;

    function do_stuff(el) {
        if (el.classList) {
            el.classList.add(className);
        } else if (!hasClass(el, className)) {
            el.className += ' ' + className;
        }
    }

    if (n.isNodeList(o)) {
        for (var i = 0, len = o.length; i < len; i++)
            do_stuff(o[i]);
    } else do_stuff(o);
}

n.removeClass = function (o, className) {
    if (!o || !className || !className.length)
        return;

    o = n.isString(o) ? document.querySelectorAll(o) : o;

    function do_stuff(el) {
        if (el.classList) {
            el.classList.remove(className);
        } else {
            var regExp = new RegExp('(?:^|\\s)' + className + '(?!\\S)', 'g');
            document.getElementById("MyElement").className = document.getElementById("MyElement").className.replace(regExp);
        }
    }

    if (n.isNodeList(o)) {
        for (var i = 0, len = o.length; i < len; i++)
            do_stuff(o[i]);
    } else do_stuff(o);
}

n.toggleClass = function (o, className) {
    if (!o || !className || !className.length)
        return;

    o = n.isString(o) ? document.querySelectorAll(o) : o;

    function do_stuff(el) {
        if (el.classList) {
            el.classList.toggle(className);
        } else {
            if (hasClass(el, className)) {
                removeClass(el, className);
            } else {
                el.className += ' ' + className;
            }
        }
    }

    if (n.isNodeList(o)) {
        for (var i = 0, len = o.length; i < len; i++)
            do_stuff(o[i]);
    } else do_stuff(o);
}

n.hasClass = function (o, className) {
    if (!o || !className || !className.length)
        return false;

    o = n.isString(o) ? document.querySelectorAll(o) : o;

    function do_stuff(el) {
        if (el.classList) {
            return el.classList.contains(className);
        } else {
            var regExp = new RegExp('(?:^|\\s)' + className + '(?!\\S)', 'g');
            return document.getElementById("MyElement").className.match(regExp);
        }
    }

    if (n.isNodeList(o)) {
        for (var i = 0, len = o.length; i < len; i++)
            if (!do_stuff(o[i]))
                return false;
    } else return do_stuff(o);

    return true;
}


n.setClass = function (o, className, state) {
    if (!state && n.hasClass(o, className)) {
        n.removeClass(o, className);
    } else if (state && !n.hasClass(o, className)) {
        n.addClass(o, className);
    }
}

n.isNodeList = function (nodes) {
    var stringRepr = Object.prototype.toString.call(nodes);

    return typeof nodes === 'object' &&
        /^\[object (HTMLCollection|NodeList|Object)\]$/.test(stringRepr) &&
        (typeof nodes.length === 'number') &&
        (nodes.length === 0 || (typeof nodes[0] === "object" && nodes[0].nodeType > 0));
}

n.startsWith = function (str, needle) {
    return str.length >= needle.length && str.substring(0, needle.length) === needle;
}

n.endsWith = function (str, needle) {
    return str.length >= needle.length && str.substring(str.length - needle.length) === needle;
}

// General purpose "contains" function
// For: strings, arrays, objects (check if property exists), nodes
n.contains = function (haystack, needle) {
    if (typeof haystack === 'string' || haystack instanceof String) {
        return haystack.indexOf(needle) > -1;
    } else if (haystack instanceof Array) {
        return n.inArray(needle, haystack);
    } else if (typeof haystack == 'object') {
        return haystack.hasOwnProperty(needle);
    } else if (n.isNode(haystack) && n.isNode(needle)) {
        return haystack.contains(needle);
    }
    return false;
}

n.isString = function (obj) {
    return typeof obj === 'string' || obj instanceof String;
}


n.hide = function (o) {
    o = n.isString(o) ? document.querySelectorAll(o) : o;

    if (n.isNodeList(o)) {
        for (var i = 0, len = o.length; i < len; i++) {
            o[i].style.display = 'none';
        }
    } else {
        o.style.display = 'none';
    }
}
n.show = function (o) {
    o = n.isString(o) ? document.querySelectorAll(o) : o;

    if (n.isNodeList(o)) {
        for (var i = 0, len = o.length; i < len; i++) {
            o[i].style.display = '';
        }
    } else {
        o.style.display = '';
    }
}