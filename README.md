# iPussy
Pussy around the world

    <div class="row justify-content-center mt-5">
      <div class="pagination">
        {% if paginator.previous_page %}
        <a href="{{ paginator.previous_page_path }}" class="previous">
          &laquo; Prev
        </a>
        {% else %}
        <span class="previous">&laquo; Prev</span>
        {% endif %}
        <span class="page_number ">
          Page: {{ paginator.page }} of {{ paginator.total_pages }}
        </span>
        {% if paginator.next_page %}
        <a href="{{ paginator.next_page_path }}" class="next">Next &raquo;</a>
        {% else %}
        <span class="next ">Next &raquo;</span>
        {% endif %}
      </div>
    </div>
