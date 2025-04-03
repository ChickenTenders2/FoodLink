from flask import Flask, render_template, request, redirect, url_for
from tool import tool

app = Flask(__name__)
tool_sql = tool()
user_id = 1

@app.route('/select_tools')
def select_tools():
    utensils = tool_sql.get_utensils()
    appliances = tool_sql.get_appliances()
    tool_ids = tool_sql.get_user_tool_ids(user_id)
    return render_template('select_utensils.html', utensils=utensils, appliances=appliances, selected_ids=tool_ids)

@app.route('/save_tools', methods=['POST'])
def save_tools():
    selected_tools = request.form.getlist('tool')
    tool_sql.save_user_tools(user_id, selected_tools)
    return redirect(url_for('select_tools'))
    # change to main page once merged
    # return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)