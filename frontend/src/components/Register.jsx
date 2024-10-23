import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';

const Register = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [first_name, setFirstname] = useState('');
    const [last_name, setLastname] = useState('');
    const [phone_number, setPhone] = useState('');
    const [activity, setActivity] = useState('');
    const [password, setPassword] = useState('');
    const [activityOptions, setActivityOptions] = useState([]);
    const [errors, setErrors] = useState({});
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false)

    // Fetch activity choices from the API
    useEffect(() => {
        const fetchActivityChoices = async () => {
            try {
                const response = await axios.get('http://127.0.0.1:8000/api/v1/activity-choices/');
                setActivityOptions(response.data);
            } catch (error) {
                console.error('Error fetching activity choices:', error);
            }
        };

        fetchActivityChoices();
    }, []);

    const handleRegistration = async (e) => {
        e.preventDefault();
        setLoading(true);

        // Debug: 
        // console.log("username:", username);
        // console.log("email:", email);
        // console.log("firstname:", firstname);
        // console.log("lastname:", lastname);
        // console.log("phone:", phone);
        // console.log("activity:", activity);
        // console.log("password:", password);
        
        const userData = {
            username, email, first_name, last_name, phone_number, activity, password
        };
        
        try {
            const response = await axios.post('http://127.0.0.1:8000/api/v1/register/', userData);
            console.log('response.data===>', response.data);
            console.log('Registration successful');
            setErrors({})
            setSuccess(true)
        } catch (error) {
            setErrors(error.response.data)
            console.log('Registration error: ', error.response.data);
        }finally{
            setLoading(false)
        }
    };

    return (
        <>
            <div className='container'>
                <div className='row justify-content-center'>
                    <div className="col-md-8 bg-light-dark p-5 rounded">
                        <h3 className='text-light text-center mb-4'>Create an Account</h3>
                        <form onSubmit={handleRegistration}>
                            <div className="row">
                                <div className="col-md-6 mb-3">
                                    <input type="text" className='form-control' placeholder='Username' value={username} onChange={(e) => setUsername(e.target.value)} />
                                    <small>{errors.username && <div className='text-danger'>{errors.username}</div>}</small>
                                </div>
                                <div className="col-md-6">
                                    <input type="email" className='form-control mb-3' placeholder='Email Address' value={email} onChange={(e) => setEmail(e.target.value)} />
                                </div>
                            </div>
                            <div className="row">
                                <div className="col-md-6">
                                    <input type="text" className='form-control mb-3' placeholder='Firstname' value={first_name} onChange={(e) => setFirstname(e.target.value)} />
                                </div>
                                <div className="col-md-6">
                                    <input type="text" className='form-control mb-3' placeholder='Lastname' value={last_name} onChange={(e) => setLastname(e.target.value)} />
                                </div>
                            </div>
                            <div className="row">
                                <div className="col-md-6">
                                    <input type="phone" className='form-control mb-3' placeholder='Phone Number' value={phone_number} onChange={(e) => setPhone(e.target.value)} />
                                </div>
                                <div className="col-md-6">
                                    {/* Select dynamically populated from backend */}
                                    <select className="form-control mb-3" value={activity} onChange={(e) => setActivity(e.target.value)} required>
                                        <option value="" disabled>Select Your Profile</option>
                                        {activityOptions.map((option, index) => (
                                            <option key={index} value={option.value}>{option.label}</option>
                                        ))}
                                    </select>

                                </div>
                            </div>
                            <div className="row">
                                <div className="col-md-12  mb-3">
                                    <input type="password" className='form-control' placeholder='Set Password' value={password} onChange={(e) => setPassword(e.target.value)} />
                                    <small>{errors.password && <div className='text-danger'>{errors.password}</div>}</small>
                                </div>
                            </div>
                            {success && <div className='alert alert-success'>Registration Successful.</div>}
                            {loading ? (
                                <div>
                                    <button type='submit' className='btn btn-info d-block mx-auto' disabled><FontAwesomeIcon icon={faSpinner} spin /> Please wait...</button>
                                </div>
                            ) :(
                                <div>
                                    <button type='submit' className='btn btn-info d-block mx-auto'>Register</button>
                                </div>
                            )}
                            
                        </form>
                    </div>
                </div>
            </div>
        </>
    );
};

export default Register;
