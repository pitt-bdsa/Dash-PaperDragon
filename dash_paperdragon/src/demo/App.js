/* eslint no-magic-numbers: 0 */
import React, { useState } from 'react';

import { DashPaperdragon } from '../lib';

const App = () => {

    const [state, setState] = useState({value:'', label:'Type Here'});
    const setProps = (newProps) => {
            setState(newProps);
        };

    return (
        <div>
            <DashPaperdragon
                setProps={setProps}
                {...state}
            />
        </div>
    )
};


export default App;
