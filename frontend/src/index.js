import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import * as serviceWorker from './serviceWorker';
import { createStore } from 'redux';
import { Provider } from 'react-redux';


let initialState = {
};

function reducer(state = initialState, action) {
    switch (action.type) {
        case 'WHOLE_STATE':
            return {
                ...state,
                ...action.payload,
            };
        case 'CHANGE_PROGRAM_NAME':
            return {
                ...state,
                programs: {
                    ...state.programs,
                    all_programs: {
                        ...state.programs.all_programs,
                        [state.programs.current_program_id]: {
                            ...state.programs.all_programs[state.programs.current_program_id],
                            name: action.payload,
                        }
                    }
                },
            };
        case 'CHANGE_PROGRAM_CODE':
            return {
                ...state,
                programs: {
                    ...state.programs,
                    all_programs: {
                        ...state.programs.all_programs,
                        [state.programs.current_program_id]: {
                            ...state.programs.all_programs[state.programs.current_program_id],
                            code: action.payload,
                        }
                    }
                },
            };
        case 'CHANGE_CURRENT_PROGRAM_ID':
            return {
                ...state,
                programs: {
                    ...state.programs,
                    current_program_id: action.payload,
                }
            };
        default:
            return state;
    }
}

let reduxStore = createStore(
    reducer,
    window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__(),
);


class NetworkApi {
    initialize({onEvent}) {
        let ws = new WebSocket(`ws://${document.domain}:4000/websocket`);
        ws.onmessage = function (msg) {
            onEvent(JSON.parse(msg.data));
        };
        // ws.send(JSON.stringify({data: 'ciao'}));
    }

    async readWholeState() {
        return await this._request('GET', '/whole_state');
    }

    async savePrograms(programs) {
        return await this._request('POST', '/command/savePrograms', programs);
    }

    async _request(method, url, payload) {
        let params = {
            method,
            headers: {
                "Content-Type": "application/json",
            },
        };
        if (payload) {
            params.body = JSON.stringify(payload);
        }
        let response = await fetch(url, params);
        if (!response.ok) {
            throw new Error(`Unexpected status code ${response.status}`);
        }
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.indexOf("application/json") !== -1) {
            return await response.json();
        } else {
            return await response.text();
        }
    }
}

let networkApi = new NetworkApi();


function onStateChanged(oldState, newState) {
    if (oldState.programs !== newState.programs) {
        networkApi.savePrograms(newState.programs)
            .catch(err => {
                console.log(err);
            });
    }
}


function startApplicationWithState(applicationState) {
    reduxStore.dispatch({ type: 'WHOLE_STATE', payload: applicationState });

    let previousState = reduxStore.getState();
    reduxStore.subscribe(function () {
        let currentState = reduxStore.getState();
        onStateChanged(previousState, currentState);
        previousState = currentState;
    });

    networkApi.initialize({
        onEvent(message) {
            reduxStore.dispatch(message);
        }
    });

    ReactDOM.render(<Provider store={reduxStore}><App /></Provider>, document.getElementById('root'));
}


networkApi.readWholeState()
    .then(function(applicationState) {
        startApplicationWithState(applicationState);
    })
    .catch(err => {
        console.log(err);
    });



// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();

