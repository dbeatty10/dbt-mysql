{% macro mysql5__split_part(string_text, delimiter_text, part_number) %}

    {% if part_number == 0 %}
        null
    {% elif part_number > 0 %}
        if(substring_index({{ string_text }}, {{ delimiter_text }}, {{ part_number }}) != substring_index({{ string_text }}, {{ delimiter_text }}, {{ part_number - 1 }}),
           substring_index(substring_index({{ string_text }}, {{ delimiter_text }}, {{ part_number }}), {{ delimiter_text }}, -1),
           null)
    {% else %}
        if(substring_index({{ string_text }}, {{ delimiter_text }}, {{ part_number }}) != substring_index({{ string_text }}, {{ delimiter_text }}, {{ part_number + 1 }}),
           substring_index(substring_index({{ string_text }}, {{ delimiter_text }}, {{ part_number }}), {{ delimiter_text }}, 1),
           null)
    {% endif %}

{% endmacro %}
