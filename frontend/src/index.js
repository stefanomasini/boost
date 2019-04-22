import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
import * as serviceWorker from './serviceWorker';
import { createStore } from 'redux';
import { Provider } from 'react-redux';
import moment from 'moment';
import debounce from 'lodash.debounce';


function now_str() {
    return moment().format("DD-MM-YYYY HH:mm:ss");
}


let initialState = {
    log_lines: [],
    testing_motors: false,
    runCode() {
        reduxStore.dispatch({ type: 'SET_PROGRAM_RUNNING', payload: true });
        networkApi.runCode()
            .catch(err => {
                reportError(err);
            });
    },
    stopCode() {
        networkApi.stopCode()
            .catch(err => {
                reportError(err);
            });
    },
    toggleAutoRun() {
        let state = reduxStore.getState();
        let autoRun = getAutoRun(state);
        networkApi.setAutoRun(!autoRun, state.programs.current_program_id)
            .then(data => {
                reduxStore.dispatch({ type: 'SET_AUTO_RUN', payload: data });
            })
            .catch(err => {
                reportError(err);
            });
    },
    getAutoRun,
    changeMotorPower: debounce(function (device, power) {
        reduxStore.dispatch({ type: 'SET_TESTING_MOTORS', payload: true });
        networkApi.changeMotorPower(device, power)
            .catch(err => {
                reportError(err);
            });
    }, 200, { maxWait: 200 }),
    resetMotors() {
        networkApi.resetMotors()
            .then(() => {
                reduxStore.dispatch({ type: 'SET_TESTING_MOTORS', payload: false });
            })
            .catch(err => {
                reportError(err);
            });
    },
};


function getAutoRun(state) {
    if (!state.auto_run || !state.auto_run.auto_run) {
        return false;
    }
    return state.programs.current_program_id === state.auto_run.program_id;
}


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
        case 'CREATE_NEW_PROGRAM':
            let new_program_id = Math.max(...Object.keys(state.programs.all_programs).map(parseInt))+1;
            return {
                ...state,
                programs: {
                    ...state.programs,
                    all_programs: {
                        ...state.programs.all_programs,
                        [new_program_id]: {
                            name: 'New program',
                            code: '',
                        },
                    },
                    current_program_id: new_program_id,
                },
            };
        case 'DELETE_CURRENT_PROGRAM':
            let new_all_programs = {...state.programs.all_programs};
            delete new_all_programs[state.programs.current_program_id];
            let _new_program_id = Math.min(...Object.keys(new_all_programs).map(parseInt));
            return {
                ...state,
                programs: {
                    ...state.programs,
                    all_programs: new_all_programs,
                    current_program_id: _new_program_id,
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
        case 'EMPTY_LOG':
            return {
                ...state,
                log_lines: [],
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
        case 'SET_AUTO_RUN':
            return {
                ...state,
                auto_run: action.payload,
            };
        case 'SET_TESTING_MOTORS':
            return {
                ...state,
                testing_motors: action.payload,
            };
        case 'CHANGE_POWER_DEFINITION':
            return {
                ...state,
                constants: {
                    ...state.constants,
                    power_definitions: replace_in_list(state.constants.power_definitions, action.payload.levelIdx, action.payload.value),
                }
            };
        case 'CHANGE_NUM_POWER_DEFINITION_LEVELS':
            return {
                ...state,
                constants: {
                    ...state.constants,
                    power_definitions: change_list_length(state.constants.power_definitions, action.payload),
                }
            };
        case 'CHANGE_RAMP_UP_TIME':
            return {
                ...state,
                constants: {
                    ...state.constants,
                    ramp_up_time_from_zero_to_max_in_sec: action.payload,
                }
            };
        default:
            return state;
    }
}

function replace_in_list(list, idx, value) {
    let new_list = [...list];
    new_list[idx] = value;
    return new_list;
}

function change_list_length(list, length) {
    let new_list = [...list];
    if (new_list.length > length) {
        new_list = new_list.slice(0, length);
    } else {
        while (new_list.length < length) {
            new_list.push(1);
        }
    }
    return new_list;
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

    async stopCode() {
        return await this._request('POST', '/command/stopProgram');
    }

    async setAutoRun(auto_run, program_id) {
        return await this._request('POST', '/command/setAutoRun', { auto_run, program_id });
    }

    async changeMotorPower(device, power) {
        return await this._request('POST', '/command/setMotorPower', { device, power });
    }

    async resetMotors() {
        return await this._request('POST', '/command/resetMotors');
    }

    async saveConstants(constants) {
        return await this._request('POST', '/command/saveConstants', constants);
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
    if (oldState.constants !== newState.constants) {
        saveNewConstants(newState.constants);
    }
}


const saveNewConstants = debounce(function (constants) {
    networkApi.saveConstants(constants)
        .catch(reportError);
}, 1000, { maxWait: 1000 });


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

