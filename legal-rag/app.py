import os
import time

from flask import  Flask,render_template,request,jsonify

from dotenv import load_dotenv

from langchain_community.document_loaders import  PyPDFLoader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


from models import embedding_model

from rag_pipeline import ask_contract_question


from evaluator import  evaluate_rag_response
from langfuse_logger import create_trace,log_ragas_scores


load_dotenv()


app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
VECTORSTORE_FOLDER = "vectorstore"



@app.route("/")
def home():

    return render_template(
        "index.html"
    )


@app.route("/upload",methods=["POST"])
def upload_pdf():

    try:

        if "pdf" not in request.files:

            return jsonify(
                {
                    "success": False,
                    "message": "No PDF uploaded"
                }
            )

        pdf_file = request.files["pdf"]

        if pdf_file.filename == "":

            return jsonify(
                {
                    "success": False,
                    "message": "No file selected"
                }
            )

        pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file.filename)

        pdf_file.save(pdf_path)
        loader = PyPDFLoader(pdf_path )

        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        chunks = splitter.split_documents( documents)

        vectorstore = FAISS.from_documents(chunks,embedding_model)

        vectorstore.save_local( VECTORSTORE_FOLDER)

        return jsonify(
            {
                "success": True,
                "message": "Contract uploaded successfully",
                "chunks_created": len(chunks)
            }
        )

    except Exception as e:

        return jsonify(
            {
                "success": False,
                "message": str(e)
            }
        )



@app.route("/ask",methods=["POST"])
def ask_question():

    try:

        question = request.form.get(
            "question"
        )

        if not question:

            return jsonify(
                {
                    "success": False,
                    "message": "Question required"
                }
            )


        start_time = time.time()


        result = ask_contract_question(question)
        latency = round(time.time() - start_time,2 )


        scores = evaluate_rag_response(
            question=question,
            answer=result["answer"],
            context=result["context"]
        )


        trace = create_trace(
            question=question,
            context=result["context"],
            prompt=result["prompt"],
            answer=result["answer"],
            latency=latency
        )


        log_ragas_scores(trace,scores)


        return jsonify(
            {
                "success": True,

                "question": question,

                "answer": result["answer"],

                "latency": latency,


                "ragas_scores": scores
            }
        )

    except Exception as e:

        return jsonify(
            {
                "success": False,
                "message": str(e)
            }
        )

if __name__ == "__main__":

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )