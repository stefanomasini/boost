import React, { useState } from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import {withStyles} from '@material-ui/core/styles';
import CssBaseline from '@material-ui/core/CssBaseline';
import Drawer from '@material-ui/core/Drawer';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import List from '@material-ui/core/List';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import Typography from '@material-ui/core/Typography';
import Divider from '@material-ui/core/Divider';
import IconButton from '@material-ui/core/IconButton';
import Checkbox from '@material-ui/core/Checkbox';
import Button from '@material-ui/core/Button';
// import Badge from '@material-ui/core/Badge';
import MenuIcon from '@material-ui/icons/Menu';
import ListIcon from '@material-ui/icons/List';
import PlayArrowIcon from '@material-ui/icons/PlayArrow';
import ArrowRightAltIcon from '@material-ui/icons/ArrowRightAlt';
import StopIcon from '@material-ui/icons/Stop';
// import Fab from '@material-ui/core/Fab';
import ChevronLeftIcon from '@material-ui/icons/ChevronLeft';
// import NotificationsIcon from '@material-ui/icons/Notifications';
// import { mainListItems, secondaryListItems } from './listItems';
// import SimpleLineChart from './SimpleLineChart';
// import SimpleTable from './SimpleTable';
import TextField from '@material-ui/core/TextField';
import ClickAwayListener from '@material-ui/core/ClickAwayListener';
import Grow from '@material-ui/core/Grow';
import Paper from '@material-ui/core/Paper';
import Popper from '@material-ui/core/Popper';
import MenuItem from '@material-ui/core/MenuItem';
import MenuList from '@material-ui/core/MenuList';

import ListItem from '@material-ui/core/ListItem';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
// import ListSubheader from '@material-ui/core/ListSubheader';
import DashboardIcon from '@material-ui/icons/Dashboard';
// import ShoppingCartIcon from '@material-ui/icons/ShoppingCart';
// import PeopleIcon from '@material-ui/icons/People';
// import BarChartIcon from '@material-ui/icons/BarChart';
import LayersIcon from '@material-ui/icons/Layers';
// import AssignmentIcon from '@material-ui/icons/Assignment';
import Slider from '@material-ui/lab/Slider';

import { connect } from 'react-redux'


import brace from 'brace';
import AceEditor from 'react-ace';

import 'brace/mode/python';
import 'brace/theme/github';


const mainListItems = (
    <div>
        <ListItem button>
            <ListItemIcon>
                <DashboardIcon/>
            </ListItemIcon>
            <ListItemText primary="Program"/>
        </ListItem>
        {/*<ListItem button>*/}
        {/*    <ListItemIcon>*/}
        {/*        <BarChartIcon/>*/}
        {/*    </ListItemIcon>*/}
        {/*    <ListItemText primary="Testing"/>*/}
        {/*</ListItem>*/}
        <ListItem button>
            <ListItemIcon>
                <LayersIcon/>
            </ListItemIcon>
            <ListItemText primary="Configuration"/>
        </ListItem>
    </div>
);


const drawerWidth = 240;

const styles = theme => ({
    root: {
        display: 'flex',
    },
    toolbar: {
        paddingRight: 24, // keep right padding when drawer closed
    },
    toolbarIcon: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        padding: '0 8px',
        ...theme.mixins.toolbar,
    },
    appBar: {
        zIndex: theme.zIndex.drawer + 1,
        transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
        }),
    },
    appBarShift: {
        marginLeft: drawerWidth,
        width: `calc(100% - ${drawerWidth}px)`,
        transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
        }),
    },
    menuButton: {
        marginLeft: 12,
        marginRight: 36,
    },
    menuButtonHidden: {
        display: 'none',
    },
    title: {
        flexGrow: 1,
    },
    drawerPaper: {
        position: 'relative',
        whiteSpace: 'nowrap',
        width: drawerWidth,
        transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
        }),
    },
    drawerPaperClose: {
        overflowX: 'hidden',
        transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
        }),
        width: theme.spacing.unit * 7,
        [theme.breakpoints.up('sm')]: {
            width: theme.spacing.unit * 9,
        },
    },
    appBarSpacer: theme.mixins.toolbar,
    content: {
        flexGrow: 1,
        flexDirection: 'column',
        height: '100vh',
        overflow: 'auto',
        padding: theme.spacing.unit * 3,
    },
    chartContainer: {
        marginLeft: -22,
    },
    tableContainer: {
        height: 320,
    },
    h5: {
        marginBottom: theme.spacing.unit * 2,
    },
    codeEditorContainer: {
        display: 'flex',
        flexDirection: 'row',
    },
    codeEditorSide: {
        width: 600,
        marginLeft: theme.spacing.unit * 3,
    },
    codeErrors: {
        marginTop: theme.spacing.unit * 2,
        padding: theme.spacing.unit,
    },
    motorSlider: {
        padding: '22px 0px',
    },
    devices: {
        display: 'flex',
        flexDirection: 'row',
        justifyContent: 'space-between',
    },
    device: {
        width: 200,
        flexGrow: 1,
        marginRight: theme.spacing.unit,
        marginBottom: 2 * theme.spacing.unit,
        padding: theme.spacing.unit,
    },
    logTable: {
        height: 500,
        overflow: 'scroll',
    }
});

class Dashboard extends React.Component {
    state = {
        open: false,
    };

    handleDrawerOpen = () => {
        this.setState({open: true});
    };

    handleDrawerClose = () => {
        this.setState({open: false});
    };

    render() {
        const {classes} = this.props;


        return (
            <div className={classes.root}>
                <CssBaseline/>
                <AppBar position="absolute" color="primary" className={classNames(classes.appBar, this.state.open && classes.appBarShift)}>
                    <Toolbar disableGutters={!this.state.open} className={classes.toolbar}>
                        <IconButton
                            color="inherit"
                            aria-label="Open drawer"
                            onClick={this.handleDrawerOpen}
                            className={classNames(
                                classes.menuButton,
                                this.state.open && classes.menuButtonHidden,
                            )}>
                            <MenuIcon/>
                        </IconButton>

                        <ProgramChoice/>

                        <Typography
                            component="h1"
                            variant="h6"
                            color="inherit"
                            noWrap
                            className={classes.title}>
                            <ProgramName/>
                        </Typography>

                    </Toolbar>
                </AppBar>
                <Drawer variant="permanent"
                        classes={{
                            paper: classNames(classes.drawerPaper, !this.state.open && classes.drawerPaperClose),
                        }}
                        open={this.state.open}>
                    <div className={classes.toolbarIcon}>
                        <IconButton onClick={this.handleDrawerClose}>
                            <ChevronLeftIcon/>
                        </IconButton>
                    </div>
                    <Divider/>
                    <List>{mainListItems}</List>
                </Drawer>
                <main className={classes.content}>
                    <div className={classes.appBarSpacer}/>
                    <CodeEditor classes={classes}/>
                    {/*<Typography variant="h4" gutterBottom component="h2">*/}
                        {/*Orders*/}
                    {/*</Typography>*/}
                    {/*<Typography component="div" className={classes.chartContainer}>*/}
                        {/*/!*<SimpleLineChart />*!/*/}
                    {/*</Typography>*/}
                    {/*<Typography variant="h4" gutterBottom component="h2">*/}
                        {/*Products*/}
                    {/*</Typography>*/}
                    {/*<div className={classes.tableContainer}>*/}
                        {/*/!*<SimpleTable />*!/*/}
                    {/*</div>*/}
                </main>
            </div>
        );
    }
}

Dashboard.propTypes = {
    classes: PropTypes.object.isRequired,
};


const ProgramChoice = connect(state => {
    let programs = [];
    for (let program_id of Object.keys(state.programs.all_programs)) {
        programs.push({
            program_id,
            name: state.programs.all_programs[program_id].name,
        });
    }
    return { programs };
}, dispatch => ({
    chooseProgramId(program_id) {
        dispatch({type: 'CHANGE_CURRENT_PROGRAM_ID', payload: program_id});
    }
}))(function ProgramChoice({ programs, chooseProgramId }) {
    const [open, setOpen] = useState(false);
    let anchorEl = null;
    function toggleOpen() {
        setOpen(!open);
    }
    function close() {
        setOpen(false);
    }
    function _choose(program_id) {
        setOpen(false);
        chooseProgramId(program_id);
    }

    return (
        <div>
            <Button
                buttonRef={node => {
                    anchorEl = node;
                }}
                color="default"
                variant="contained"
                style={{ marginRight: 20 }}
                aria-owns={open ? 'menu-list-grow' : undefined}
                aria-haspopup="true"
                onClick={toggleOpen}>
                <ListIcon/>
            </Button>
            <Popper open={open} anchorEl={anchorEl} transition disablePortal>
                {({ TransitionProps, placement }) => (
                  <Grow
                    {...TransitionProps}
                    id="menu-list-grow"
                    style={{ transformOrigin: placement === 'bottom' ? 'center top' : 'center bottom' }}>
                    <Paper>
                      <ClickAwayListener onClickAway={close}>
                        <MenuList>
                            { programs.map(program => <MenuItem key={program.program_id} onClick={() => _choose(program.program_id)}>{program.name}</MenuItem>) }
                        </MenuList>
                      </ClickAwayListener>
                    </Paper>
                  </Grow>
                )}
            </Popper>
        </div>
    );
});


console.log(`Brace version: ${brace.version}`);


const CodeEditor = connect(state => ({
    programCode: state.programs.all_programs[state.programs.current_program_id].code,
    compilation_errors: state.compilation_errors,
    program_running: state.program_running,
    log_lines: state.log_lines,
    device_names: state.device_names,
    motor_power: state.motor_power || {},
    shaft_position: state.shaft_position || {},
    auto_run: state.getAutoRun(state),
    testing_motors: state.testing_motors,
    // Functions
    runCode: state.runCode,
    stopCode: state.stopCode,
    toggleAutoRun: state.toggleAutoRun,
    changeMotorPower: state.changeMotorPower,
    resetMotors: state.resetMotors,
}), dispatch => ({
    setProgramCode(code) {
        dispatch({type: 'CHANGE_PROGRAM_CODE', payload: code});
    },
}))(function CodeEditor({ classes, programCode, setProgramCode, compilation_errors, program_running, log_lines, device_names,
                          runCode, stopCode, motor_power, shaft_position, auto_run, toggleAutoRun, changeMotorPower, testing_motors, resetMotors }) {
    let canRun = compilation_errors.length === 0;
    log_lines = [...log_lines];
    log_lines.reverse();
    return (
        <div className={classes.codeEditorContainer}>
            <AceEditor mode="python"
                       theme="github"
                       value={programCode}
                       readOnly={program_running}
                       onChange={setProgramCode}
                       debounceChangePeriod={300}
                       name="UNIQUE_ID_OF_DIV"
                       editorProps={{$blockScrolling: true}}/>
            <div className={classes.codeEditorSide}>
                <div className={classes.devices}>
                    { device_names.map(device => <Device key={device} device={device}
                                                         shaft_position={shaft_position[device]}
                                                         motor_power={motor_power[device]}
                                                         classes={classes}
                                                         program_running={program_running}
                                                         onChange={changeMotorPower} />)}
                </div>

                { testing_motors
                    ? <Button color="secondary" variant="contained" size="large" onClick={resetMotors}>
                          <StopIcon />
                          Reset motors
                      </Button>
                    : program_running
                    ? <Button color="secondary" variant="contained" size="large" onClick={stopCode}>
                                              <StopIcon />
                                              Stop program
                                          </Button>
                    : <Button color="primary" variant="contained" size="large" disabled={!canRun} onClick={runCode}>
                          <PlayArrowIcon />
                          Run program
                      </Button>}

                { !program_running && <span>
                </span>}
                <Typography><Checkbox disabled={program_running} checked={auto_run} onChange={toggleAutoRun}/> Run automatically at start-up</Typography>

                { compilation_errors.length > 0 && <Paper className={classes.codeErrors}>
                    <Typography variant="h5" color="secondary" gutterBottom>
                        Errors in the program:
                    </Typography>
                    <Table>
                        <TableBody>
                            { compilation_errors.map((error, idx) => <TableRow key={idx}>
                                <TableCell><Typography variant="body1"><i>Line {error.line_num}</i></Typography></TableCell>
                                <TableCell><Typography>{error.message}</Typography></TableCell>
                            </TableRow>) }
                        </TableBody>
                    </Table>
                </Paper>}

                { log_lines.length > 0 && <Paper className={classes.codeErrors}>
                    <Typography variant="h5" gutterBottom>
                        Log:
                    </Typography>
                    <div className={classes.logTable}>
                        <Table padding="dense">
                            <TableBody>
                            { log_lines.map((logline, idx) => <TableRow key={idx} style={{ height: 30 }}>
                                <TableCell style={{ width: 180 }}><Typography variant="body1"><i>{logline.ts}</i></Typography></TableCell>
                                <TableCell style={{ width: 80 }}><Typography><i>{logline.type}</i></Typography></TableCell>
                                <TableCell><Typography>{logline.message}</Typography></TableCell>
                            </TableRow>) }
                            </TableBody>
                        </Table>
                    </div>
                </Paper>}

            </div>
        </div>
    );
});

CodeEditor.propTypes = {
    classes: PropTypes.object.isRequired,
};


function Device({ device, shaft_position, motor_power, classes, program_running, onChange }) {
    if (!shaft_position) {
        shaft_position = {
            angle: 0,
            position: '?',
            undef: true,
        };
    }
    if (typeof motor_power === typeof undefined || motor_power === null) {
        motor_power = 0;
    }
    return <Paper className={classes.device}>
        <table><tbody><tr>
            <td>
                <Typography variant="h5">{device}</Typography>
            </td>
            <td>
                <ArrowRightAltIcon fontSize="large" style={ {transform: `rotate(${90 - shaft_position.angle}deg)`, color: shaft_position.undef ? 'gray' : null} }/>
            </td>
            { shaft_position.undef ? <td>
                <Typography style={{ color: 'gray' }}>N/A</Typography>
            </td> : <td>
                <Typography>{ shaft_position.angle } deg ({ shaft_position.angle })</Typography>
            </td> }
        </tr></tbody></table>
        <Typography>Motor: {parseInt(motor_power * 100) / 100}</Typography>
        <Slider classes={{ container: classes.motorSlider }}
                value={motor_power * 50 + 50}
                onChange={(event, value) => { if (!program_running) { onChange(device, (value - 50) / 50); } }}
                disabled={program_running} />
    </Paper>;
}

const ProgramName = connect(state => ({
    programName: state.programs.all_programs[state.programs.current_program_id].name,
}), dispatch => ({
    setProgramName(programName) {
        dispatch({type: 'CHANGE_PROGRAM_NAME', payload: programName});
    }
}))(({ programName, setProgramName }) => {
    const [state, setState] = useState({ editing: false });

    function onBlur() {
        setProgramName(state.value);
        setState({ editing: false });
    }

    return (
        state.editing
            ? <TextField value={state.value} onChange={e => setState({ editing: true, value: e.target.value })} autoFocus={true} onBlur={onBlur}/>
            : <span onClick={() => setState({ editing: true, value: programName })}>{programName}</span>
    );
});


export default withStyles(styles)(Dashboard);
