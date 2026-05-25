import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { Users, Activity, Calendar, Shield } from 'lucide-react'
import { getAdminStats, getAdminPredictions } from '../utils/api'
import { useAuth } from '../context/AuthContext'

const COLORS = ['#22c55e', '#16a34a', '#15803d', '#f59e0b', '#ef4444', '#8b5cf6']

export default function Admin() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [predictions, setPredictions] = useState([])

  useEffect(() => {
    if (user?.is_admin) {
      getAdminStats().then((r) => setStats(r.data)).catch(console.error)
      getAdminPredictions().then((r) => setPredictions(r.data)).catch(console.error)
    }
  }, [user])

  if (!user?.is_admin) {
    return (
      <div className="text-center py-32">
        <Shield className="w-16 h-16 mx-auto text-gray-400 mb-4" />
        <p>Admin access required</p>
        <Link to="/" className="btn-primary mt-4 inline-block">Go Home</Link>
      </div>
    )
  }

  const chartData = stats
    ? Object.entries(stats.disease_distribution || {}).map(([name, value]) => ({
        name: name.length > 20 ? name.slice(0, 20) + '...' : name,
        value,
      }))
    : []

  return (
    <div className="max-w-7xl mx-auto px-6 py-32">
      <h1 className="font-display text-4xl font-bold mb-8 flex items-center gap-3">
        <Shield className="w-10 h-10 text-plant-500" /> Admin Dashboard
      </h1>

      {stats && (
        <div className="grid md:grid-cols-3 gap-6 mb-10">
          {[
            { icon: Users, label: 'Total Users', value: stats.total_users },
            { icon: Activity, label: 'Total Predictions', value: stats.total_predictions },
            { icon: Calendar, label: 'Today', value: stats.predictions_today },
          ].map(({ icon: Icon, label, value }) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="glass-card p-6"
            >
              <Icon className="w-8 h-8 text-plant-500 mb-2" />
              <p className="text-gray-500 text-sm">{label}</p>
              <p className="text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
            </motion.div>
          ))}
        </div>
      )}

      <div className="grid lg:grid-cols-2 gap-8">
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4">Disease Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={chartData}>
              <XAxis dataKey="name" tick={{ fontSize: 10 }} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#22c55e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="glass-card p-6">
          <h3 className="font-semibold mb-4">Distribution Pie</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                {chartData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-card p-6 mt-8">
        <h3 className="font-semibold mb-4">Recent Predictions</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b dark:border-gray-700">
                <th className="pb-2">ID</th>
                <th className="pb-2">Disease</th>
                <th className="pb-2">Confidence</th>
                <th className="pb-2">Date</th>
              </tr>
            </thead>
            <tbody>
              {predictions.slice(0, 20).map((p) => (
                <tr key={p.id} className="border-b dark:border-gray-800">
                  <td className="py-2">{p.id}</td>
                  <td>{p.disease_name}</td>
                  <td>{p.confidence}%</td>
                  <td>{new Date(p.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
