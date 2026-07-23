import { useRef, useState } from 'react';
import html2canvas from 'html2canvas';
import { jsPDF } from 'jspdf';
import ReactMarkdown from 'react-markdown';
import { toast } from 'react-toastify';
import './ReportView.css';

export default function ReportView({ report }) {
  const [open, setOpen] = useState(true);
  const [downloading, setDownloading] = useState(false);
  const reportRef = useRef(null);
  const downloadPdf = async () => {
    setDownloading(true);
    try {
      const canvas = await html2canvas(reportRef.current, { backgroundColor: '#171b39', scale: 2, useCORS: true });
      const image = canvas.toDataURL('image/png');
      const pdf = new jsPDF('p', 'mm', 'a4');
      const width = 190;
      const height = canvas.height * width / canvas.width;
      let position = 10;
      let remaining = height;
      pdf.addImage(image, 'PNG', 10, position, width, height);
      remaining -= 277;
      while (remaining > 0) {
        position = remaining - height + 10;
        pdf.addPage();
        pdf.addImage(image, 'PNG', 10, position, width, height);
        remaining -= 277;
      }
      pdf.save(`${report.full_name.replace(/[^a-z0-9]/gi, '-')}-kundli-report.pdf`);
      toast.success('PDF downloaded');
    } catch {
      toast.error('Could not create PDF');
    } finally {
      setDownloading(false);
    }
  };
  return <article className="report card"><div className="report-head"><div><span className="eyebrow">Kundli report</span><h2>{report.full_name}</h2><p>{report.city} · {report.birth_date} · {report.birth_time}</p></div><div className="report-actions"><button className="secondary" onClick={downloadPdf} disabled={downloading}>{downloading ? 'Preparing PDF…' : 'Download PDF'}</button><button className="secondary" onClick={() => setOpen(!open)}>{open ? 'Collapse' : 'Expand'}</button></div></div>{open && <div ref={reportRef}><ReactMarkdown>{report.content}</ReactMarkdown></div>}</article>;
}
