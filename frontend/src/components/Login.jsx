import React, { useContext, useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';
import {useNavigate} from 'react-router-dom';
import { AuthContext } from '../AuthProvider';


const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [error, setError] = useState('');
  const {isLoggedIn, setIsLoggedIn} = useContext(AuthContext);


  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Validation on the customer's side
    if (!email || !password) {
        setError('Email and password are required');
        setLoading(false);
        return;
      }

    const userData = {email, password}
    console.log('userData===>', userData);

    try{
        const response = await axios.post('https://stockpredictionbackendapp.srv506012.hstgr.cloud/api/v1/token/', userData);
        localStorage.setItem('accessToken', response.data.access)
        localStorage.setItem('refreshToken', response.data.refresh)
        console.log('Login successful');
        setIsLoggedIn(true);
        navigate('/dashboard');
    } catch (error) {
        console.error('Invalid credentials.');
        setError('Invalid credentials');
      } finally {
        setLoading(false);
      }
    };


  return (
    <>
    <div className='container'>
        <div className='row justify-content-center'>
            <div className="col-md-8 bg-light-dark p-5 rounded">
                <h3 className='text-light text-center mb-4'>Login our portal</h3>
                <form onSubmit={handleLogin}>
                    <div className="row">
                         <div className="col-md-12 mb-3">
                            <input type="email" className='form-control mb-3' placeholder='Email Address' value={email} onChange={(e) => setEmail(e.target.value)} />
                        </div>
                    </div>
                    <div className="row">
                        <div className="col-md-12  mb-3">
                            <input type="password" className='form-control' placeholder='Set Password' value={password} onChange={(e) => setPassword(e.target.value)} />
                          
                        </div>
                    </div>

                    {error && <div className='text-danger'>{error}</div>}

                    {loading ? (
                        <div>
                            <button type='submit' className='btn btn-info d-block mx-auto' disabled><FontAwesomeIcon icon={faSpinner} spin /> Logging in...</button>
                        </div>
                    ) :(
                        <div>
                            <button type='submit' className='btn btn-info d-block mx-auto'>Login</button>
                        </div>
                    )}
                    
                </form>
            </div>
        </div>
    </div>
</>
  )
}

export default Login