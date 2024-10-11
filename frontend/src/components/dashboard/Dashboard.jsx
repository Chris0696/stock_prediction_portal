import {useEffect, useState} from 'react'
import axiosInstance from '../../AxiosInstance';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSpinner } from '@fortawesome/free-solid-svg-icons';

const Dashboard = () => {

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
        try{
            const response = await axiosInstance.post('/predict/', {
                ticker: ticker
            });
            console.log(response.data);
            const backendRoot = import.meta.env.VITE_BACKEND_ROOT
            const plotUrl = `${backendRoot}${response.data.plot_img}`
            const ma100Url = `${backendRoot}${response.data.plot_100_dma}`
            const ma200Url = `${backendRoot}${response.data.plot_200_dma}`
            const predictionUrl = `${backendRoot}${response.data.plot_prediction}`
            
            //console.log(plotUrl);
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
            console.error('There was an error making th API request', error)
        }finally {
            setLoading(false);
        }
    }

    return (
        <div className='container'>
            <div className="row">
                <div className="col-md-6 mx-auto">
                    <form onSubmit={handleSubmit}>
                        <input type="text" className='form-control' placeholder='Enter Stock Ticker' 
                        onChange={(e) => setTicker(e.target.value)} required
                        />
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