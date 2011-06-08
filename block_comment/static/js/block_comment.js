(function ($) {
    var methods = {
        init: function (options) {
            var blocks, save_block_comment, widget, get_block_html,
                get_index_for_block, update_bubble,
                successHandler, errorHandler,
                $this = this,
                orig_html = $this.html(),
                orig_dom = $(orig_html).filter("*"),
                data = $this.data('block_comment'),
                settings = {
                    commentOnContainer: ".block-comment-container",
                    blockCommentClass: ".block-comment",
                    commentClass: ".comment",
                    commentContainer: ".comments",
                    commentForm: "#standard-comment-form",
                    clickWhileOpen: "close",
                    error: function (jqXHR, textStatus, errorThrown, data) {
                        var current_widget = $("#comment-widget"),
                            label;
                        if (!data) {
                            data = {'errors': {'comment': errorThrown}};
                        }
                        for (key in data.errors) {
                            if (data.errors.hasOwnProperty(key)) {
                                label = current_widget.find("label[for='id_" + key + "']");
                                if (!label.length) {
                                    label = current_widget.find('label:first');
                                }
                                label.addClass("error").append("<span class='error'>&nbsp;(" + data.errors[key] + ")</span>");
                            }
                            current_widget.find("textarea").focus();
                        }
                    },
                    success: function (data, textStatus, jqXHR) {}
                };

            update_bubble = function (block, container) {
                var bubble = block.find(".bubble");
                if (bubble.length) {
                    bubble.fadeOut(150).queue(function () {
                        var el = $(this);
                        el.text(parseInt(bubble.text(), 10) + 1);
                        el.fadeIn(150);
                        el.dequeue();
                    });
                } else {
                    $('<span class="bubble">' +
                        container.find(settings.commentClass).length +
                        '</span>').hide().prependTo(block).fadeIn(250);
                }
            };

            get_block_html = function (block_index) {
                return orig_dom.eq(block_index).clone().wrap("<div></div>").parent().html();
            }

            get_index_for_block = function (regarding) {
                return orig_html.indexOf(regarding);
            };

            successHandler = function (data, textStatus, jqXHR) {
                var current_widget = $("#comment-widget"),
                    block, comment, comment_container, last_comment;
                current_widget.find("button, textarea").attr("disabled", "");
                if (data.status) {
                    switch (data.status) {
                    case 500:
                        settings.error(jqXHR, textStatus, '', data);
                        break;
                    default:
                        break;
                    }
                } else {
                    block = $("#" + $(data).attr("id").split("_")[0]);
                    comment = $(data).hide();
                    comment.find(".regarding").hide();
                    comment_container = block.next(settings.commentOnContainer);
                    last_comment = comment_container.find(".comment:last");
                    if (last_comment.length) {
                        last_comment.after(comment);
                    } else {
                        comment_container.prepend(comment);
                    }
                    update_bubble(block, comment_container);
                    comment.slideDown();
                    comment_container.find("textarea").val("");
                    settings.success(data, textStatus, jqXHR)
                }
            };

            errorHandler = function (jqXHR, textStatus, errorThrown) {
                settings.error(jqXHR, textStatus, errorThrown);
            };

            if (options) {
                $.extend(settings, options);
            }


            save_block_comment = function (evt) {
                // placeholder for AJAX save
                var form = $(evt.target),
                    comment = form.find("textarea").val(),
                    data = form.data(),
                    extra_params = $.param([
                        {name:"index", value:data.index},
                        {name:"regarding", value:data.regarding},
                    ]);
                if (!settings.url) {
                    settings.url = $(settings.commentForm).attr("action");
                }
                $.ajax({
                    type: "POST",
                    url: settings.url,
                    data: form.serialize() + "&" + extra_params,
                    success: successHandler,
                    error: errorHandler
                });
                form.find("button, textarea").attr("disabled", "disabled");
                return false;
            };

            // Initialize our block-commentable element if it hasn't been already
            if (!data || data.initialized !== false) {
                $this.data('block_comment', {
                    'target': $this,
                    'initialized': true,
                    'original_html': $this.html()
                });
                widget = $(settings.commentForm).clone().attr("id", "comment-widget");
                $(settings.commentForm + " textarea").after("<p class='help-text'>" +
                        "You may also comment on individual sections by " +
                        "clicking on the text you wish to respond to above.</p>");
                $this.find(" > *").each(function (index, item) {
                    var el = $(item);
                    el.attr("id", "i" + get_index_for_block(get_block_html(index)));
                    el.addClass("block");
                    $("<div class='block-comment-container comments'>" +
                            "<div class='triangle'></div>" +
                            "</div>").hide().insertAfter(el);
                });
                blocks = $this.find(".block");
                blocks.hover(function (evt) {
                    $(evt.target).closest(".block").addClass("highlight");
                }, function (evt) {
                    $(evt.target).closest(".block").removeClass("highlight");
                });

                // Comment widget interaction
                blocks.click(function (evt) {
                    var el = $(evt.target).closest(".block"),
                        container = el.next(settings.commentOnContainer),
                        current_selection = $(".selected"),
                        new_widget = widget.clone(),
                        show_comments, regarding, index, block_index;

                    block_index = el.parent().children(":not(" + settings.commentOnContainer + ")").index(el);
                    regarding = get_block_html(block_index);
                    index = get_index_for_block(regarding);

                    show_comments = function () {
                            new_widget.data({
                                "regarding": regarding,
                                "index": index
                            });
                            new_widget.submit(save_block_comment);
                            container.find("#comment-widget").remove();
                            container.append(new_widget).slideDown().find("textarea").focus();
                            $(this).dequeue();
                        };
                    if (!el.hasClass("selected")) {
                        el.addClass("selected");
                        if (current_selection.length) {
                            current_selection.removeClass("selected");
                            current_selection.next(settings.commentOnContainer)
                                .slideUp()
                                .queue(show_comments);
                        } else {
                            show_comments();
                        }
                    } else {
                        switch (settings.clickWhileOpen) {
                        case "remind":
                            if (typeof container.effect === "function") {
                                container.effect("shake", {times: 2, distance: 5}, 100);
                            } else {
                                $.error("The remind option for clickWhileOpen requires jQuery UI");
                            }
                            break;
                        case "close":
                            container.slideUp().queue(function () {
                                var el = $(this);
                                el.find("#comment-widget").remove();
                                el.dequeue();
                            });
                            el.removeClass("selected");
                            break;
                        default:
                            $.error("Invalid value for the clickWhileOpen option.");
                            break;
                        }
                    }
                });

                // Initialize existing comments
                $(settings.commentContainer).find(".regarding").hide();
                $(settings.commentContainer + " " + settings.blockCommentClass)
                    .each(function (index, item) {
                        var comment = $(item),
                            hash = comment.find(".regarding a").attr("href"),
                            block = $(hash),
                            container = block.next(settings.commentOnContainer);
                        comment.appendTo(container);
                        update_bubble(block, container);
                    });
            }

            return this;
        }
    };

    $.fn.block_comment = function (method) {
        // Method calling logic
        if (methods[method]) {
            return methods[method].apply(this, Array.prototype.slice.call(arguments, 1));
        }
        else if (typeof method === 'object' || ! method) {
            return methods.init.apply(this, arguments);
        }
        else {
            $.error('Method ' + method + ' does not exist on jQuery.block_comment');
        }
    };
}(jQuery));
