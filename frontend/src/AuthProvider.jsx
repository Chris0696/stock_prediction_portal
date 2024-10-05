import { useContext, useState, createContext } from 'react'

// Create The context
const AuthContext = createContext();

const AuthProvider = ({children}) => {

    const [isLoggedIn, setIsLoggedIn] = useState(
        !!localStorage.getItem('accessToken')
    )

  return (
    <AuthContext.Provider value={{isLoggedIn, setIsLoggedIn}}>
        {children}
    </AuthContext.Provider>
  )
}

export default AuthProvider
export {AuthContext};