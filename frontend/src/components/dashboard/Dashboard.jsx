import {useEffect, useState} from 'react'
import axiosInstance from 'src/axiosInstance';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';

const Dashboard = () => {
    const [rates, setRates] = useState([]); 
    const [ticker, setTicker] = useState('');
    const [error, setError] = useState();
    const [loading, setLoading] = useState(false);
    const [plot, setPlot] = useState();
    const [ma100, setMA100] = useState();
    const [ma200, setMA200] = useState();
    const [prediction, setPrediction] = useState();
    const [mse, setMSE] = useState();
    const [rmse, setRMSE] = useState();
    const [r2, setR2] = useState();
    
    const [start_date, setStartDate] = useState('2023-01-01'); // Start date by default

    const currentDate = new Date().toISOString().split('T')[0]; // Format YYYY-MM-DD
    const [end_date, setEndDate] = useState(currentDate); //  Current date
    
    const [ticker_period, setTickerPeriod] = useState('1DAY'); // Période  by default
    


    useEffect(() => {
        
        const fetchProtectedData = async () =>{
            
            try {
                const response = await axiosInstance.get('/protected-view/');
                console.log('Protected data:', response.data);

            }catch (error) {
                console.error('Error fetching protected  data:', error)
            }
        
        };
        fetchProtectedData();
        
    }, [])

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        // Date validation
        if (new Date(start_date) > new Date(end_date)) {
            setError("The start date cannot be greater than the end date.");
            setLoading(false);
            return; //  Do not submit form if error
            
            
        } else if (new Date(end_date) > new Date(currentDate)) {
            setError("The end date cannot be greater than the current date.");
            setLoading(false);
            return; // Do not submit form if error
        };

        setLoading(true);
        setError('');  // Reset errors before query
        
            
        try {
            
            const response = await axiosInstance.post('/predict/', {
                ticker: ticker,  // Example : 'EUR/USD'
                start_date: start_date,  // Format : 'YYYY-MM-DD'
                end_date: end_date,  // Format : 'YYYY-MM-DD'
                ticker_period: ticker_period  // Example : '1DAY'
            });

            
            console.log(response.data);

            
            setRates(response.data.rates);
            const backendRoot = import.meta.env.VITE_BACKEND_ROOT
            const plotUrl = `${backendRoot}${response.data.plot_img}`
            const ma100Url = `${backendRoot}${response.data.plot_100_dma}`
            const ma200Url = `${backendRoot}${response.data.plot_200_dma}`
            const predictionUrl = `${backendRoot}${response.data.plot_prediction}`
            console.log(plotUrl);
            setPlot(plotUrl)
            setMA100(ma100Url)
            setMA200(ma200Url)
            setPrediction(predictionUrl)
            setMSE(response.data.mse)
            setRMSE(response.data.rmse)
            setR2(response.data.r2)

            // Set plots
            if(response.data.error){
                setError(response.data.error)
            }
            
        }catch (error) {
            console.error('There was an error making th API request', error);
            
        }finally {
            setLoading(false);
        }
    };

    return (
        <div className='container'>
            <div className="row">
                <div className="col-md-6 mx-auto">
                    <form onSubmit={handleSubmit}>
                        <input type="text" className='form-control' placeholder='Ex: BRL/EUR, USDT/EUR, EUR/USD, GBP/USD, BTC/USD XAU/USD etc.' onChange={(e) => setTicker(e.target.value.toUpperCase())} value={ticker} required />
                        
                    <div className='mt-3'>
                        <label>Start Date:</label>
                        <input type="date" className="form-control" onChange={(e) => setStartDate(e.target.value)} value={start_date} required/>
                    </div>
                        
                    <div className='mt-3'>
                        <label>End Date:</label>
                        <input type="date" className="form-control" onChange={(e) => setEndDate(e.target.value)} value={end_date} required/>

                    </div>
                        
                    <div className='mt-3'>
                        <label>Ticker Period:</label>
                        <select className='form-control' onChange={(e) => setTickerPeriod(e.target.value)} value={ticker_period}>
                            <option value="1DAY">1 Day</option>
                            <option value="1HRS">1 Hour</option>
                            <option value="1MIN">1 Minute</option>
                        </select>
                    </div>

                    <small>{error && <div className='text-danger'>{error}</div>}</small>
                    
                    <button type='submit' className='btn btn-info mt-3 d-block mx-auto'>
                    {loading ? <span><FontAwesomeIcon icon={faSpinner} spin /> Please Wait...</span>: 'See Prediction'}
                    </button>
                    </form>
                </div>

                {/* Print prediction plot */}

                {prediction && (
                    <div className='prediction mt-5'>
                    <div className='p-3'>
                        {plot && (
                            <img src={plot} style={{ maxWidth: '100%' }}/>
                        )}
                    </div>
                    <div className="p-3">
                        {ma100 && (
                            <img src={ma100} style={{ maxWidth: '100%' }} />
                        )}
                    </div>
                    <div className="p-3">
                        {ma200 && (
                            <img src={ma200} style={{ maxWidth: '100%' }} />
                        )}
                    </div>
                    <div className="p-3">
                        {prediction && (
                            <img src={prediction} style={{ maxWidth: '100%' }} />
                        )}
                    </div>

                    <div className="text-light p-3">
                        <h4><u>Model Evaluation</u></h4>
                        <p><em><b>Mean Squared Error (MSE)</b></em>: {mse}</p>
                        <p><em><b>Root Mean Squared Error (RMSE)</b></em>: {rmse}</p>
                        <p><em><b>R-Squared</b></em>: {r2}</p>
                    </div>

                </div>
                )}
                

            </div>
        </div>
    )
}

export default Dashboard