import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import * as serviceWorker from './serviceWorker';
import { createStore } from 'redux';
import { Provider } from 'react-redux';
import moment from 'moment';


function now_str() {
    return moment().format("DD-MM-YYYY HH:mm:ss");
}


let initialState = {
    log_lines: [],
    runCode() {
        reduxStore.dispatch({ type: 'SET_PROGRAM_RUNNING', payload: true });
        networkApi.runCode()
            .catch(err => {
                reportError(err);
            });
    },
    stopCode() {
        // reduxStore.dispatch({ type: 'SET_PROGRAM_RUNNING', payload: true });
        // networkApi.runCode()
        //     .catch(err => {
        //         reportError(err);
        //     });
    },
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
        case 'CLEAR_COMPILATION_ERRORS':
            return {
                ...state,
                compilation_errors: [],
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
        case 'COMPILATION_ERRORS':
            return {
                ...state,
                compilation_errors: action.payload.errors,
            };
        case 'RUNTIME_ERROR':
            return {
                ...state,
                log_lines: state.log_lines.concat([{type: 'RuntimeError', message: action.payload, ts: now_str()}]),
            };
        case 'FRONTEND_ERROR':
            return {
                ...state,
                log_lines: state.log_lines.concat([{type: 'FrontendError', message: action.payload, ts: now_str()}]),
            };
        case 'SERVER_LOG':
            return {
                ...state,
                log_lines: state.log_lines.concat([{type: 'Server', message: action.payload, ts: now_str()}]),
            };
        case 'SET_PROGRAM_RUNNING':
            return {
                ...state,
                program_running: action.payload,
            };
        case 'MOTOR_POWER':
            return {
                ...state,
                motor_power: {
                    ...(state.motor_power || {}),
                    [action.payload.device]: action.payload.power,
                },
            };
        case 'SHAFT_POSITION':
            return {
                ...state,
                shaft_position: {
                    ...(state.shaft_position || {}),
                    [action.payload.device]: { angle: action.payload.angle, position: action.payload.position },
                },
            };
        default:
            return state;
    }
}

let reduxStore = createStore(
    reducer,
    window.__REDUX_DEVTOOLS_EXTENSION__ && window.__REDUX_DEVTOOLS_EXTENSION__(),
);

function reportError(err) {
    console.log(err);
    reduxStore.dispatch({ type: 'FRONTEND_ERROR', payload: err.message });
}

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

    async runCode() {
        return await this._request('POST', '/command/runProgram');
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
        if (response.status === 400) {
            let error = new Error('HTTP Response code 400');
            error.code_400_message = await response.text();
            throw error;
        }
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
            .then(result => {
                reduxStore.dispatch({ type: 'CLEAR_COMPILATION_ERRORS' });
            })
            .catch(err => {
                if (err.code_400_message) {
                    console.log(err.code_400_message);
                } else {
                    reportError(err);
                }
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

