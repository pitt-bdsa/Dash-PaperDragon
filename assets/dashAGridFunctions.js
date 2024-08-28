

var dagfuncs = window.dashAgGridFunctions = window.dashAgGridFunctions || {};


// Put the following in the dashAgGridComponentFunctions.js file in the assets folder
// ## NOTE one is for cellRenderers and the other is for cellEditors..
// -----------
var dagcomponentfuncs = (window.dashAgGridComponentFunctions = window.dashAgGridComponentFunctions || {});


dagcomponentfuncs.colorCellRenderer = function (props) {
    console.log(props);
    // TO DO is make this more intelligent
    try {
        var color = props.value[1]; // props is an array for the palette
    } catch (error) {
        console.error("Error accessing props.value[1]:", error);
        var color = "#ff00ff";
    }
    return React.createElement(
        'div',
        { style: { backgroundColor: color, width: '100%', height: '100%' } },
        null
    );

}


dagfuncs.eyeCellRenderer = class {
    // gets called once before the renderer is used
    init(params) {
        // create the cell
        this.eInput = document.createElement('i');
        if (params.value) {
            this.eInput.className = 'fa fa-eye';
        } else {
            this.eInput.className = 'fa fa-eye-slash';
        }
        this.eInput.style.height = 'var(--ag-row-height)';
        this.eInput.style.fontSize = 'calc(var(--ag-font-size) + 1px)';
    }
    // gets called once when grid ready to insert the element
    getGui() {
        return this.eInput;
    }
    // gets called whenever the user gets the cell to refresh
    refresh(params) {
        if (params.value) {
            this.eInput.className = 'fa fa-eye';
        } else {
            this.eInput.className = 'fa fa-eye-slash';
        }
    }
}


dagfuncs.NumberInput = class {
    // gets called once before the renderer is used
    init(params) {
        // create the cell
        this.eInput = document.createElement('input');
        this.eInput.value = params.value;
        this.eInput.style.height = 'var(--ag-row-height)';
        this.eInput.style.fontSize = 'calc(var(--ag-font-size) + 1px)';
        this.eInput.style.borderWidth = 0;
        this.eInput.style.width = '95%';
        this.eInput.type = "number";
        this.eInput.min = params.min;
        this.eInput.max = params.max;
        this.eInput.step = params.step || "any";
        this.eInput.required = params.required;
        this.eInput.placeholder = params.placeholder || "";
        this.eInput.name = params.name;
        this.eInput.disabled = params.disabled;
        this.eInput.title = params.title || ""
    }

    // gets called once when grid ready to insert the element
    getGui() {
        return this.eInput;
    }

    // focus and select can be done after the gui is attached
    afterGuiAttached() {
        this.eInput.focus();
        this.eInput.select();
    }

    // any cleanup we need to be done here
    destroy() {
        // but this example is simple, no cleanup, we could
        // even leave this method out as it's optional
    }

    // if true, then this editor will appear in a popup
    isPopup() {
        // and we could leave this method out also, false is the default
        return false;
    }
}

