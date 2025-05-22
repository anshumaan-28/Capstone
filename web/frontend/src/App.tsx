import { ChakraProvider, Box, Flex, VStack } from '@chakra-ui/react'
import { Header } from './components/Header'
import { SpectralBands } from './components/SpectralBands'
import { Visualization } from './components/Visualization'
import { BandManipulations } from './components/BandManipulations'
import { DataStatistics } from './components/DataStatistics'
import { VisualizationProvider } from './contexts/VisualizationContext'

function App() {
  return (
    <ChakraProvider>
      <VisualizationProvider>
        <Box minH="100vh" bg="gray.800" color="white">
          <Header />
          <Box width="100%" px={4} py={8}>
            <Flex gap={8} flexWrap={{ base: "wrap", lg: "nowrap" }} width="100%">
              <VStack spacing={8} flex="1" minW={{ base: "100%", lg: "300px" }} maxW={{ lg: "350px" }}>
                <SpectralBands />
                <BandManipulations />
              </VStack>
              <VStack spacing={8} flex="3" width="100%">
                <Visualization />
                <DataStatistics />
              </VStack>
            </Flex>
          </Box>
        </Box>
      </VisualizationProvider>
    </ChakraProvider>
  )
}

export default App
